import json
import mimetypes
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
DATA_DIR = ROOT / "data"
REPORT_DIR = DATA_DIR / "reports"
CONFIG_PATH = DATA_DIR / "funds.json"


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload):
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_text(path: Path):
    return path.read_text(encoding="utf-8")


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler, status, text, content_type="text/plain; charset=utf-8"):
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def not_found(handler):
    json_response(handler, 404, {"error": "not_found"})


def bad_request(handler, message):
    json_response(handler, 400, {"error": "bad_request", "message": message})


def load_summary():
    context_path = REPORT_DIR / "latest_context.json"
    plan_path = REPORT_DIR / "latest_trade_plan.json"
    report_path = REPORT_DIR / "latest_daily_report.md"
    dashboard_path = REPORT_DIR / "latest_dashboard.html"

    context = read_json(context_path) if context_path.exists() else None
    trade_plan = read_json(plan_path) if plan_path.exists() else None
    return {
        "context": context,
        "trade_plan": trade_plan,
        "files": {
            "report": str(report_path),
            "dashboard": str(dashboard_path),
            "has_report": report_path.exists(),
            "has_dashboard": dashboard_path.exists(),
        },
    }


def run_script(script: str, timeout: int):
    command = [sys.executable, str(ROOT / "scripts" / script)]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "script": script,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "script": script,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
            "message": "联网更新超时，已改用本地缓存继续生成报告。",
        }


def run_analysis(mode: str):
    if mode == "online":
        scripts = [("fetch_funds.py", 60), ("build_context.py", 30), ("generate_report.py", 30)]
    elif mode == "cached":
        scripts = [("build_context.py", 30), ("generate_report.py", 30)]
    else:
        raise ValueError("mode must be cached or online")

    output = []
    warnings = []
    for script, timeout in scripts:
        step = run_script(script, timeout)
        output.append(step)
        if step["timed_out"] and script == "fetch_funds.py":
            warnings.append(step["message"])
            continue
        if step["returncode"] != 0:
            return {
                "ok": False,
                "mode": mode,
                "message": f"{script} 执行失败，请查看终端日志。",
                "steps": output,
                "warnings": warnings,
                "summary": load_summary(),
            }
    return {
        "ok": True,
        "mode": mode,
        "steps": output,
        "warnings": warnings,
        "message": warnings[0] if warnings else "报告已生成。",
        "summary": load_summary(),
    }


class AppHandler(BaseHTTPRequestHandler):
    server_version = "FundAssistantWeb/0.1"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            json_response(self, 200, {"ok": True})
            return
        if path == "/api/config":
            json_response(self, 200, read_json(CONFIG_PATH))
            return
        if path == "/api/summary":
            json_response(self, 200, load_summary())
            return
        if path == "/api/report/latest":
            report_path = REPORT_DIR / "latest_daily_report.md"
            if not report_path.exists():
                not_found(self)
                return
            text_response(self, 200, read_text(report_path), "text/markdown; charset=utf-8")
            return
        if path == "/dashboard":
            dashboard_path = REPORT_DIR / "latest_dashboard.html"
            if not dashboard_path.exists():
                not_found(self)
                return
            text_response(self, 200, read_text(dashboard_path), "text/html; charset=utf-8")
            return

        self.serve_static(path)

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/config":
            not_found(self)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            validate_config(payload)
        except ValueError as exc:
            bad_request(self, str(exc))
            return
        except Exception as exc:
            bad_request(self, f"Invalid JSON: {exc}")
            return

        write_json(CONFIG_PATH, payload)
        json_response(self, 200, {"ok": True, "config": payload})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            not_found(self)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            mode = payload.get("mode", "cached")
            result = run_analysis(mode)
            json_response(self, 200 if result["ok"] else 500, result)
        except Exception as exc:
            json_response(self, 500, {"ok": False, "error": "run_failed", "message": str(exc)})

    def serve_static(self, path: str):
        if path == "/":
            path = "/index.html"
        relative = path.lstrip("/")
        target = (WEB_DIR / relative).resolve()
        try:
            target.relative_to(WEB_DIR.resolve())
        except ValueError:
            not_found(self)
            return
        if not target.exists() or not target.is_file():
            not_found(self)
            return

        body = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if target.suffix in {".html", ".css", ".js"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def validate_config(payload):
    if not isinstance(payload, dict):
        raise ValueError("Config must be an object")
    profile = payload.get("profile")
    funds = payload.get("funds")
    if not isinstance(profile, dict):
        raise ValueError("profile must be an object")
    if not isinstance(funds, list):
        raise ValueError("funds must be a list")
    for index, fund in enumerate(funds, start=1):
        if not fund.get("code"):
            raise ValueError(f"fund #{index} is missing code")
        if not fund.get("name"):
            raise ValueError(f"fund #{index} is missing name")
        target_ratio = fund.get("target_ratio")
        if target_ratio is not None and not 0 <= float(target_ratio) <= 1:
            raise ValueError(f"fund #{index} target_ratio must be between 0 and 1")
        holding = fund.get("holding_amount")
        if holding is not None and float(holding) < 0:
            raise ValueError(f"fund #{index} holding_amount cannot be negative")


def main():
    host = "127.0.0.1"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Fund Assistant Web is running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()

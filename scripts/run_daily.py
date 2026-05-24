import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(script_name: str):
    script = ROOT / "scripts" / script_name
    print(f"\n==> python {script}", flush=True)
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def main():
    run("fetch_funds.py")
    run("build_context.py")
    run("generate_report.py")


if __name__ == "__main__":
    main()

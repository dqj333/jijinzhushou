import json
import math
import re
import statistics
import time
from dataclasses import dataclass
from datetime import date, datetime
from html import unescape
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import URLError
from urllib.request import Request, urlopen
try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PRICE_DIR = DATA_DIR / "prices"
REPORT_DIR = DATA_DIR / "reports"
CONFIG_PATH = DATA_DIR / "funds.json"


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)


@dataclass
class NavPoint:
    nav_date: str
    nav: float
    accumulated_nav: float | None
    daily_return_pct: float | None


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_text(url: str, referer: str | None = None, timeout: int = 5, retries: int = 1) -> str:
    headers = {"User-Agent": USER_AGENT}
    if referer:
        headers["Referer"] = referer
    if requests is not None:
        last_error = None
        session = requests.Session()
        session.trust_env = False
        for attempt in range(retries):
            try:
                response = session.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                response.encoding = response.encoding or "utf-8"
                return response.text
            except Exception as exc:
                last_error = exc
                if attempt == retries - 1:
                    break
                time.sleep(0.5 * (attempt + 1))
        if last_error is not None:
            raise last_error
    request = Request(url, headers=headers)
    last_error = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=timeout) as response:
                raw = response.read()
            break
        except (OSError, URLError) as exc:
            last_error = exc
            if attempt == retries - 1:
                raise
            time.sleep(0.5 * (attempt + 1))
    else:
        raise last_error
    for encoding in ("utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_history(code: str, per: int = 260) -> list[NavPoint]:
    api_points = fetch_history_json_api(code, per)
    if api_points:
        return api_points

    points: list[NavPoint] = []
    seen_dates = set()
    page = 1
    page_size = 20
    while len(points) < per:
        params = urlencode({"type": "lsjz", "code": code, "page": page, "per": page_size})
        url = f"https://fundf10.eastmoney.com/F10DataApi.aspx?{params}"
        try:
            text = fetch_text(url, referer=f"https://fundf10.eastmoney.com/jjjz_{code}.html")
        except Exception:
            if points:
                break
            raise
        rows = re.findall(r"<tr>(.*?)</tr>", text, flags=re.S)
        page_points = parse_history_rows(rows)
        new_points = [item for item in page_points if item.nav_date not in seen_dates]
        if not new_points:
            break
        points.extend(new_points)
        seen_dates.update(item.nav_date for item in new_points)
        page += 1
        time.sleep(0.05)
    points.sort(key=lambda item: item.nav_date, reverse=True)
    return points[:per]


def fetch_history_json_api(code: str, per: int = 60) -> list[NavPoint]:
    points = []
    seen_dates = set()
    page_size = 20
    page = 1
    while len(points) < per:
        params = urlencode({"fundCode": code, "pageIndex": page, "pageSize": page_size})
        url = f"https://api.fund.eastmoney.com/f10/lsjz?{params}"
        text = fetch_text(url, referer="https://fundf10.eastmoney.com/", timeout=12, retries=1)
        data = json.loads(text)
        rows = data.get("Data", {}).get("LSJZList", [])
        if not rows:
            break
        before = len(points)
        for row in rows:
            try:
                if row["FSRQ"] in seen_dates:
                    continue
                points.append(
                    NavPoint(
                        nav_date=row["FSRQ"],
                        nav=float(row["DWJZ"]),
                        accumulated_nav=to_float(str(row.get("LJJZ") or "")),
                        daily_return_pct=to_percent(str(row.get("JZZZL") or "")),
                    )
                )
                seen_dates.add(row["FSRQ"])
            except (KeyError, ValueError, TypeError):
                continue
        if len(points) == before:
            break
        page += 1
    points.sort(key=lambda item: item.nav_date, reverse=True)
    return points[:per]


def parse_history_rows(rows: list[str]) -> list[NavPoint]:
    points: list[NavPoint] = []
    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
        values = [clean_html(cell) for cell in cells]
        if len(values) < 4 or not re.match(r"\d{4}-\d{2}-\d{2}", values[0]):
            continue
        try:
            points.append(
                NavPoint(
                    nav_date=values[0],
                    nav=float(values[1]),
                    accumulated_nav=to_float(values[2]),
                    daily_return_pct=to_percent(values[3]),
                )
            )
        except ValueError:
            continue
    return points


def fetch_estimate(code: str) -> dict | None:
    url = f"https://fundgz.1234567.com.cn/js/{code}.js?rt={int(time.time() * 1000)}"
    try:
        text = fetch_text(url, referer="https://fund.eastmoney.com/")
    except Exception:
        return None
    match = re.search(r"jsonpgz\((.*)\);?$", text.strip())
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def clean_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return unescape(value).strip()


def to_float(value: str) -> float | None:
    value = value.strip()
    if not value or value == "--":
        return None
    return float(value)


def to_percent(value: str) -> float | None:
    value = value.strip().replace("%", "")
    if not value or value == "--":
        return None
    return float(value)


def pct_change(latest: float, base: float | None) -> float | None:
    if base is None or base == 0:
        return None
    return (latest / base - 1) * 100


def value_at(points: list[NavPoint], trading_days: int) -> float | None:
    if len(points) <= trading_days:
        return None
    return points[trading_days].nav


def percentile_position(values: list[float], current: float) -> float | None:
    if not values:
        return None
    low = min(values)
    high = max(values)
    if math.isclose(low, high):
        return 50.0
    return (current - low) / (high - low) * 100


def max_drawdown(values: list[float]) -> float | None:
    if not values:
        return None
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = (value / peak - 1) * 100
        worst = min(worst, drawdown)
    return worst


def annualized_volatility(points: list[NavPoint], days: int = 60) -> float | None:
    series = list(reversed(points[: days + 1]))
    if len(series) < 10:
        return None
    returns = []
    for previous, current in zip(series, series[1:]):
        if previous.nav:
            returns.append(current.nav / previous.nav - 1)
    if len(returns) < 2:
        return None
    return statistics.stdev(returns) * math.sqrt(252) * 100


def latest_report_date() -> str:
    return date.today().isoformat()


def safe_round(value, digits: int = 2):
    if value is None:
        return None
    return round(value, digits)


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")

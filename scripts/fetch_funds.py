from fund_data import CONFIG_PATH, PRICE_DIR, fetch_estimate, fetch_history, read_json, write_json


def main():
    config = read_json(CONFIG_PATH)
    results = []
    failures = []
    for fund in config["funds"]:
        code = fund["code"]
        price_file = PRICE_DIR / f"{code}.json"
        try:
            history = fetch_history(code)
            estimate = None
        except Exception as exc:
            if price_file.exists():
                cached = read_json(price_file)
                history = cached.get("history", [])
                estimate = cached.get("estimate")
                failures.append(f"{code} {fund.get('name')}: fetch failed, used cache ({exc})")
                print(f"{code} {fund.get('name')}: fetch failed, used cache", flush=True)
                continue
            failures.append(f"{code} {fund.get('name')}: fetch failed, no cache ({exc})")
            print(f"{code} {fund.get('name')}: fetch failed, no cache", flush=True)
            continue
        payload = {
            "code": code,
            "configured_name": fund.get("name"),
            "estimate": estimate,
            "history": [
                {
                    "date": item.nav_date,
                    "nav": item.nav,
                    "accumulated_nav": item.accumulated_nav,
                    "daily_return_pct": item.daily_return_pct,
                }
                for item in history
            ],
        }
        write_json(PRICE_DIR / f"{code}.json", payload)
        results.append((code, fund.get("name"), len(history), history[0].nav_date if history else None))
        print(f"{code} {fund.get('name')}: fetched {len(history)} rows, latest={history[0].nav_date if history else None}", flush=True)

    print(f"Done. Updated {len(results)} fund price files.", flush=True)
    if failures:
        print("Failures:", flush=True)
        for item in failures:
            print(f"- {item}", flush=True)


if __name__ == "__main__":
    main()

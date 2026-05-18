#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from time import sleep
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener


DEFAULT_INDEX_CODES = ["000001", "399001", "399006", "000688"]
FIELDS = "f12,f14,f2,f3,f4,f6,f8,f15,f16,f17,f18,f62"
STOCK_NAME_CACHE = Path(__file__).resolve().parents[1] / "references" / "stock_name_cache.json"


def market_prefix(code: str, *, index: bool = False) -> str:
    if index:
        return "1" if code.startswith(("000", "880")) else "0"
    return "1" if code.startswith(("5", "6", "9")) else "0"


def secids(codes: list[str], *, index: bool = False) -> str:
    return ",".join(f"{market_prefix(code, index=index)}.{code}" for code in codes)


def fetch_snapshot(codes: list[str], *, index: bool = False) -> dict:
    params = urlencode(
        {
            "fltt": "2",
            "invt": "2",
            "fields": FIELDS,
            "secids": secids(codes, index=index),
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        },
        safe=",:",
    )
    url = f"https://push2.eastmoney.com/api/qt/ulist.np/get?{params}"
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://quote.eastmoney.com/",
        },
    )
    opener = build_opener(ProxyHandler({}))
    payload = None
    for attempt in range(3):
        try:
            with opener.open(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            break
        except Exception:
            if attempt < 2:
                sleep(0.8 * (attempt + 1))

    if payload is None:
        ps = (
            "$OutputEncoding=[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
            "$headers=@{'User-Agent'='Mozilla/5.0'; 'Referer'='https://quote.eastmoney.com/'};"
            f"$r=Invoke-RestMethod -Uri '{url}' -Headers $headers -TimeoutSec 20;"
            "$r | ConvertTo-Json -Depth 6"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=35,
            check=True,
        )
        payload = json.loads(completed.stdout)

    rows = []
    for item in (payload.get("data") or {}).get("diff") or []:
        rows.append(
            {
                "code": item.get("f12"),
                "name": item.get("f14"),
                "latest": item.get("f2"),
                "change_pct": item.get("f3"),
                "change": item.get("f4"),
                "turnover": item.get("f6"),
                "turnover_rate": item.get("f8"),
                "high": item.get("f15"),
                "low": item.get("f16"),
                "open": item.get("f17"),
                "previous_close": item.get("f18"),
                "main_net_inflow_eastmoney": item.get("f62"),
            }
        )
    return {
        "source": "eastmoney_push2",
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "is_index": index,
        "rows": rows,
    }


def cache_fallback_payload(codes: list[str], *, index: bool, error: Exception) -> dict:
    cache = {}
    if STOCK_NAME_CACHE.exists():
        try:
            cache = json.loads(STOCK_NAME_CACHE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    return {
        "source": "eastmoney_push2_unavailable",
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "is_index": index,
        "error": str(error),
        "note": "行情快照未取到，不能把本结果当作价格/成交额来源；仅可用于已缓存代码简称参考。",
        "rows": [
            {
                "code": code,
                "name": cache.get(code, ""),
                "latest": None,
                "change_pct": None,
                "turnover": None,
                "turnover_rate": None,
                "main_net_inflow_eastmoney": None,
            }
            for code in codes
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Eastmoney index/stock snapshots for fact cards.")
    parser.add_argument("--codes", nargs="*", default=[], help="A-share or index codes, e.g. 000988 301666")
    parser.add_argument("--indices", action="store_true", help="Fetch default major A-share indices")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codes = args.codes or (DEFAULT_INDEX_CODES if args.indices else [])
    if not codes:
        raise SystemExit("Provide --codes or --indices")

    exit_code = 0
    try:
        payload = fetch_snapshot(codes, index=args.indices)
    except Exception as exc:
        payload = cache_fallback_payload(codes, index=args.indices, error=exc)
        exit_code = 2
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

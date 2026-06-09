#!/usr/bin/env python3
"""Unified optional data-source entrypoint for stock-wechat-writer.

The script keeps AKShare, efinance, and BaoStock optional. Missing packages or
failing upstream APIs return structured errors instead of blocking the recap.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
from datetime import date
from typing import Any


INDEX_ALIASES = {
    "sh000001": {"ak_sina": "sh000001", "name": "上证指数"},
    "sz399001": {"ak_sina": "sz399001", "name": "深证成指"},
    "sz399006": {"ak_sina": "sz399006", "name": "创业板指"},
    "sh000688": {"ak_sina": "sh000688", "name": "科创50"},
}


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def ok(source: str, data: Any) -> dict[str, Any]:
    return {"source": source, "ok": True, "data": data}


def fail(source: str, err: Exception | str) -> dict[str, Any]:
    return {"source": source, "ok": False, "error": str(err)}


def normalize_code_for_baostock(code: str) -> str:
    raw = code.strip().lower()
    if "." in raw:
        return raw
    if raw.startswith(("6", "9")):
        return f"sh.{raw}"
    return f"sz.{raw}"


def normalize_code_plain(code: str) -> str:
    raw = code.strip().lower()
    if "." in raw:
        return raw.split(".")[-1]
    if raw.startswith(("sh", "sz")):
        return raw[2:]
    return raw


def akshare_indices() -> dict[str, Any]:
    import akshare as ak

    df = ak.stock_zh_index_spot_sina()
    rows = []
    for code, meta in INDEX_ALIASES.items():
        match = df[df["代码"].astype(str).str.lower() == code]
        if match.empty:
            rows.append({"code": code, "name": meta["name"], "error": "not_found"})
            continue
        item = match.iloc[0].to_dict()
        rows.append(
            {
                "code": code,
                "name": item.get("名称") or meta["name"],
                "price": item.get("最新价"),
                "change_pct": item.get("涨跌幅"),
                "change": item.get("涨跌额"),
                "turnover": item.get("成交额"),
                "volume": item.get("成交量"),
            }
        )
    return {"indices": rows}


def akshare_stock_history(code: str, start: str, end: str) -> dict[str, Any]:
    import akshare as ak

    df = ak.stock_zh_a_hist(symbol=normalize_code_plain(code), period="daily", start_date=start, end_date=end, adjust="")
    return {
        "code": normalize_code_plain(code),
        "rows": len(df),
        "columns": list(map(str, df.columns)),
        "tail": df.tail(5).to_dict(orient="records"),
    }


def efinance_stock_history(code: str, start: str, end: str) -> dict[str, Any]:
    import efinance as ef

    df = ef.stock.get_quote_history(normalize_code_plain(code), beg=start, end=end)
    return {
        "code": normalize_code_plain(code),
        "rows": len(df),
        "columns": list(map(str, df.columns)),
        "tail": df.tail(5).to_dict(orient="records"),
    }


def baostock_stock_history(code: str, start: str, end: str) -> dict[str, Any]:
    import baostock as bs
    import pandas as pd

    lg = bs.login()
    try:
        if getattr(lg, "error_code", "0") != "0":
            raise RuntimeError(f"baostock login failed: {lg.error_code} {lg.error_msg}")
        rs = bs.query_history_k_data_plus(
            normalize_code_for_baostock(code),
            "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turnpct,pctChg",
            start_date=f"{start[:4]}-{start[4:6]}-{start[6:]}",
            end_date=f"{end[:4]}-{end[4:6]}-{end[6:]}",
            frequency="d",
            adjustflag="3",
        )
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if rs.error_code != "0":
            raise RuntimeError(f"baostock query failed: {rs.error_code} {rs.error_msg}")
        df = pd.DataFrame(rows, columns=rs.fields)
        return {
            "code": normalize_code_for_baostock(code),
            "rows": len(df),
            "columns": list(map(str, df.columns)),
            "tail": df.tail(5).to_dict(orient="records"),
        }
    finally:
        bs.logout()


def fetch_history(provider: str, code: str, start: str, end: str) -> dict[str, Any]:
    if provider == "akshare":
        return ok("akshare.stock_zh_a_hist", akshare_stock_history(code, start, end))
    if provider == "efinance":
        return ok("efinance.stock.get_quote_history", efinance_stock_history(code, start, end))
    if provider == "baostock":
        return ok("baostock.query_history_k_data_plus", baostock_stock_history(code, start, end))
    return fail(provider, f"unsupported provider: {provider}")


def history_worker(queue: mp.Queue, provider: str, code: str, start: str, end: str) -> None:
    try:
        queue.put(fetch_history(provider, code, start, end))
    except Exception as exc:
        queue.put(fail(provider, exc))


def fetch_history_with_timeout(provider: str, code: str, start: str, end: str, timeout: int) -> dict[str, Any]:
    context = mp.get_context("spawn")
    queue: mp.Queue = context.Queue()
    process = context.Process(target=history_worker, args=(queue, provider, code, start, end), daemon=True)
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join(5)
        return fail(provider, f"{provider} timeout after {timeout}s")
    if not queue.empty():
        return queue.get()
    return fail(provider, f"{provider} worker exited without result, exitcode={process.exitcode}")


def probe() -> dict[str, Any]:
    providers = {
        "akshare": module_available("akshare"),
        "efinance": module_available("efinance"),
        "baostock": module_available("baostock"),
        "pandas": module_available("pandas"),
    }
    return {"providers": providers}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch A-share data from AKShare, efinance, and BaoStock.")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--indices", action="store_true", help="Fetch core index snapshots with AKShare")
    parser.add_argument("--history", metavar="CODE", help="Fetch daily K history for a stock/index code")
    parser.add_argument("--provider", choices=["auto", "akshare", "efinance", "baostock"], default="auto")
    parser.add_argument("--start", default=date.today().replace(day=1).strftime("%Y%m%d"))
    parser.add_argument("--end", default=date.today().strftime("%Y%m%d"))
    parser.add_argument("--timeout", type=int, default=45, help="Per-provider timeout seconds for history fetches")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results: dict[str, Any] = {"probe": probe()}

    if args.probe and not args.indices and not args.history:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
        return 0

    if args.indices:
        if module_available("akshare"):
            try:
                results["indices"] = ok("akshare.stock_zh_index_spot_sina", akshare_indices())
            except Exception as exc:
                results["indices"] = fail("akshare.stock_zh_index_spot_sina", exc)
        else:
            results["indices"] = fail("akshare.stock_zh_index_spot_sina", "akshare not installed")

    if args.history:
        providers = [args.provider] if args.provider != "auto" else ["akshare", "efinance", "baostock"]
        history = []
        for provider in providers:
            if not module_available(provider):
                history.append(fail(provider, f"{provider} not installed"))
                continue
            history.append(fetch_history_with_timeout(provider, args.history, args.start, args.end, args.timeout))
        results["history"] = history

    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

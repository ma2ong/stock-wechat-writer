#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_LEDGER = Path("output/stock_review_judgements.jsonl")


def parse_date(value: str) -> str:
    return date.fromisoformat(value).isoformat()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no} is not valid JSON") from exc
        if isinstance(item, dict):
            rows.append(item)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def append_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def cmd_add(args: argparse.Namespace) -> int:
    review_date = date.fromisoformat(parse_date(args.date))
    due_date = review_date + timedelta(days=args.window_days)
    row = {
        "id": args.id or f"{review_date.isoformat()}-{args.market_type}",
        "date": review_date.isoformat(),
        "due_date": due_date.isoformat(),
        "market_type": args.market_type,
        "core_judgement": args.core_judgement,
        "mainline": args.mainline,
        "watch_condition": args.watch_condition,
        "risk_level": args.risk_level,
        "invalidation": args.invalidation,
        "article_path": args.article_path,
        "outcome": "",
        "score": None,
        "review_note": "",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    append_row(args.ledger, row)
    print(f"added judgement: {row['id']}")
    return 0


def cmd_due(args: argparse.Namespace) -> int:
    rows = load_jsonl(args.ledger)
    today = date.fromisoformat(parse_date(args.as_of))
    due_rows = [
        row for row in rows
        if not row.get("outcome") and date.fromisoformat(str(row.get("due_date"))) <= today
    ]
    if not due_rows:
        print("no due judgements")
        return 0
    for row in due_rows:
        print(f"- {row.get('id')} | {row.get('date')} | {row.get('mainline')} | due {row.get('due_date')}")
        print(f"  判断: {row.get('core_judgement')}")
        print(f"  观察: {row.get('watch_condition')}")
        print(f"  失效: {row.get('invalidation')}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    rows = load_jsonl(args.ledger)
    found = False
    for row in rows:
        if row.get("id") != args.id:
            continue
        row["outcome"] = args.outcome
        row["score"] = args.score
        row["review_note"] = args.note
        row["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
        found = True
        break
    if not found:
        raise ValueError(f"judgement id not found: {args.id}")
    write_jsonl(args.ledger, rows)
    print(f"reviewed judgement: {args.id}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    rows = load_jsonl(args.ledger)
    reviewed = [row for row in rows if row.get("outcome")]
    if not reviewed:
        print("no reviewed judgements")
        return 0

    total = len(reviewed)
    by_outcome: dict[str, int] = {}
    scores: list[float] = []
    for row in reviewed:
        outcome = str(row.get("outcome") or "unknown")
        by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
        score = row.get("score")
        if isinstance(score, (int, float)):
            scores.append(float(score))

    print(f"reviewed: {total}")
    for outcome, count in sorted(by_outcome.items()):
        print(f"- {outcome}: {count}")
    if scores:
        avg = sum(scores) / len(scores)
        print(f"avg_score: {avg:.2f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and review stock recap judgements.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("--id")
    add.add_argument("--date", required=True)
    add.add_argument("--market-type", required=True)
    add.add_argument("--core-judgement", required=True)
    add.add_argument("--mainline", required=True)
    add.add_argument("--watch-condition", required=True)
    add.add_argument("--risk-level", default="medium", choices=["low", "medium", "high"])
    add.add_argument("--invalidation", required=True)
    add.add_argument("--article-path", default="")
    add.add_argument("--window-days", type=int, default=5)
    add.set_defaults(func=cmd_add)

    due = sub.add_parser("due")
    due.add_argument("--as-of", default=date.today().isoformat())
    due.set_defaults(func=cmd_due)

    review = sub.add_parser("review")
    review.add_argument("--id", required=True)
    review.add_argument("--outcome", required=True, choices=["hit", "miss", "neutral", "invalidated"])
    review.add_argument("--score", type=float)
    review.add_argument("--note", default="")
    review.set_defaults(func=cmd_review)

    summary = sub.add_parser("summary")
    summary.set_defaults(func=cmd_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

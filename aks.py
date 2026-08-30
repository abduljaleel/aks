#!/usr/bin/env python3
"""AK$ ledger clerk. Writes both public ledger paths so they cannot drift.

AK$ is studio store credit. Not legal tender. Not a coin. Not an investment.
"""

from __future__ import annotations

import argparse
import calendar
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def last_uhi_period(ledger: dict) -> str | None:
    periods = [
        t.get("period")
        for t in ledger.get("tx") or []
        if t.get("type") == "uhi" and t.get("period")
    ]
    return periods[-1] if periods else None


def next_period(yyyy_mm: str) -> str:
    year, month = (int(part) for part in yyyy_mm.split("-"))
    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{month + 1:02d}"


def month_label(yyyy_mm: str) -> str:
    year, month = (int(part) for part in yyyy_mm.split("-"))
    return f"{calendar.month_name[month]} {year}"


def build_status(ledger: dict) -> dict:
    last = last_uhi_period(ledger)
    nxt = next_period(last) if last else None
    first = next(
        (
            t.get("period")
            for t in ledger.get("tx") or []
            if t.get("type") == "uhi" and t.get("period")
        ),
        None,
    )
    parts = []
    if nxt:
        parts.append(f"{month_label(nxt)} UHI is not yet paid")
    if first:
        parts.append(f"{month_label(first)} was the first cycle")
    note = ". ".join(parts) + "." if parts else "No UHI cycle has been posted."
    return {
        "last_uhi_period": last,
        "next_uhi_period": nxt,
        "period": "calendar month, Australia/Melbourne",
        "enrolled": list(ledger.get("enrolled") or []),
        "note": note,
        "legal": "AK$ is studio store credit. Not legal tender. Not a security. Not for public sale as an investment.",
    }


def write_public_files(root: Path, ledger: dict) -> None:
    dump(root / "data" / "ledger.json", ledger)
    dump(root / "ledger.json", ledger)
    dump(root / "data" / "status.json", build_status(ledger))


def load_canonical(root: Path) -> dict:
    path = root / "data" / "ledger.json"
    if not path.is_file():
        path = root / "ledger.json"
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: Path) -> int:
    data = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
    published = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
    if data != published:
        print("ledger.json and data/ledger.json have drifted", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write AK$ public ledger files.")
    parser.add_argument("--check", action="store_true", help="exit 1 if public ledgers differ")
    parser.add_argument("--root", type=Path, default=HERE)
    args = parser.parse_args(argv)
    if args.check:
        return check(args.root)
    write_public_files(args.root, load_canonical(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

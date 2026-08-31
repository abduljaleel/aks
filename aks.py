#!/usr/bin/env python3
"""AK$ ledger clerk. Writes both public ledger paths so they cannot drift.

AK$ is studio store credit. Not legal tender. Not a coin. Not an investment.
"""

from __future__ import annotations

import argparse
import calendar
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
MELBOURNE = ZoneInfo("Australia/Melbourne")


class UhiError(ValueError):
    """Standing UHI cycle cannot be posted."""


def money(value) -> str:
    return f"{Decimal(str(value)).quantize(Decimal('0.01')):.2f}"


def current_melbourne_period(now: datetime | None = None) -> str:
    local = (now or datetime.now(timezone.utc)).astimezone(MELBOURNE)
    return f"{local.year}-{local.month:02d}"


def utc_stamp(now: datetime | None = None) -> str:
    instant = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return instant.strftime("%Y-%m-%dT%H:%M:%SZ")


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def uhi_periods(ledger: dict) -> list[str]:
    return sorted(
        t.get("period")
        for t in ledger.get("tx") or []
        if t.get("type") == "uhi" and t.get("period")
    )


def last_uhi_period(ledger: dict) -> str | None:
    periods = uhi_periods(ledger)
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
    periods = uhi_periods(ledger)
    last = periods[-1] if periods else None
    first = periods[0] if periods else None
    nxt = next_period(last) if last else None
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


def post_uhi(
    root: Path,
    period: str | None = None,
    *,
    now: datetime | None = None,
    at: str | None = None,
) -> dict:
    """Credit every enrolled account for one Melbourne calendar month.

    Refuses if that period is already posted, is not the next unpaid cycle,
    or has not started in Australia/Melbourne. Same rate for every enrollee.
    """
    ledger = load_canonical(root)
    enrolled = list(ledger.get("enrolled") or [])
    if not enrolled:
        raise UhiError("no enrolled accounts")
    policy = ledger.get("policy") or {}
    raw_rate = policy.get("rate_monthly")
    if raw_rate in (None, ""):
        raise UhiError("policy.rate_monthly is missing")
    rate = money(raw_rate)
    last = last_uhi_period(ledger)
    due = next_period(last) if last else current_melbourne_period(now)
    period = period or due
    if period in uhi_periods(ledger):
        raise UhiError(f"UHI {period} is already posted")
    if period != due:
        raise UhiError(f"next unpaid UHI period is {due}, not {period}")
    current = current_melbourne_period(now)
    if period > current:
        raise UhiError(f"UHI {period} is not due until Australia/Melbourne {period}")
    balances = dict(ledger.get("balances") or {})
    for account in enrolled:
        prior = Decimal(str(balances.get(account, "0.00")))
        balances[account] = money(prior + Decimal(rate))
    if "treasury" in balances:
        balances["treasury"] = money(balances["treasury"])
    tx = {
        "type": "uhi",
        "id": f"uhi-{period}",
        "period": period,
        "rate": rate,
        "to": enrolled,
        "reason": f"Universal High Income {month_label(period)} cycle",
        "at": at or utc_stamp(now),
    }
    ledger = dict(ledger)
    ledger["balances"] = balances
    ledger["tx"] = list(ledger.get("tx") or []) + [tx]
    write_public_files(root, ledger)
    return ledger


def check(root: Path) -> int:
    try:
        data = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
        published = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
        status = json.loads((root / "data" / "status.json").read_text(encoding="utf-8"))
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 1
    if data != published:
        print("ledger.json and data/ledger.json have drifted", file=sys.stderr)
        return 1
    if status != build_status(data):
        print("data/status.json does not match the ledger", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write AK$ public ledger files.")
    parser.add_argument("command", nargs="?", choices=("uhi",), help="uhi: post the next unpaid cycle")
    parser.add_argument("--period", help="YYYY-MM to post; defaults to the next unpaid period")
    parser.add_argument("--check", action="store_true", help="exit 1 if public ledgers differ")
    parser.add_argument("--root", type=Path, default=HERE)
    args = parser.parse_args(argv)
    if args.check:
        return check(args.root)
    if args.command == "uhi":
        try:
            posted = post_uhi(args.root, period=args.period)
        except UhiError as exc:
            print(exc, file=sys.stderr)
            return 1
        print(f"posted {posted['tx'][-1]['id']}")
        return 0
    write_public_files(args.root, load_canonical(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

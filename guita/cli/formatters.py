"""CLI output formatting."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from guita.app.service import PeriodStats
from guita.cli.charts import render_xy_chart
from guita.domain.money import ZERO, format_money
from guita.domain.models import Account, AccountBalance, Transaction, TransactionType

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"


def use_color(*, stream: object | None = None) -> bool:
    """Color when stdout is a TTY and NO_COLOR is unset."""
    if os.environ.get("NO_COLOR", ""):
        return False
    if os.environ.get("GUITA_FORCE_COLOR", ""):
        return True
    target = stream if stream is not None else sys.stdout
    return hasattr(target, "isatty") and bool(target.isatty())


def color_text(text: str, amount: Decimal, *, enabled: bool | None = None) -> str:
    if enabled is None:
        enabled = use_color()
    if not enabled:
        return text
    if amount > ZERO:
        return f"{_GREEN}{text}{_RESET}"
    if amount < ZERO:
        return f"{_RED}{text}{_RESET}"
    return text


def display_money(
    amount: Decimal,
    *,
    signed: bool = False,
    width: int | None = None,
    color: bool | None = None,
) -> str:
    text = format_money(amount, signed=signed)
    if width is not None:
        text = f"{text:>{width}}"
    return color_text(text, amount, enabled=color)


def _local_day(value: datetime) -> str:
    # Date-only chart points are naive calendar days; leave them unshifted.
    if value.tzinfo is None:
        return value.strftime("%b %d")
    return value.astimezone().strftime("%b %d")


def _bar(value: Decimal, maximum: Decimal, *, width: int = 20, color: bool | None = None) -> str:
    if maximum <= ZERO or value == ZERO:
        bar = "·" * width if value == ZERO else "░" * 1 + " " * (width - 1)
        return color_text(bar[:width].ljust(width), value, enabled=color)

    units = int(
        (abs(value) / maximum * Decimal(width)).to_integral_value(rounding=ROUND_HALF_UP)
    )
    units = max(1, min(width, units))
    filled = "█" * units
    empty = " " * (width - units)
    return color_text(filled + empty, value, enabled=color)


def format_balances(balances: list[AccountBalance], total: Decimal) -> str:
    lines = ["Guita", "──────────────────────────────", ""]
    if not balances:
        lines.append("No accounts yet.")
        lines.append("Add one with: guita account add <name> USD")
        return "\n".join(lines)

    width = max(len(b.account.name) for b in balances)
    width = max(width, 5)
    for item in balances:
        marker = "" if item.account.active else " (inactive)"
        lines.append(
            f"{item.account.name:<{width}}  {display_money(item.balance, width=12)}{marker}"
        )
    lines.append("──────────────────────────────")
    lines.append(f"{'Total':<{width}}  {display_money(total, width=12)}")
    return "\n".join(lines)


def format_accounts(accounts: list[Account]) -> str:
    if not accounts:
        return "No accounts."
    lines = []
    for account in accounts:
        status = "active" if account.active else "inactive"
        lines.append(f"{account.name} — {account.currency} ({status})")
    return "\n".join(lines)


def _type_label(tx: Transaction) -> str:
    if tx.type is TransactionType.ADDITION:
        return "Addition"
    if tx.type is TransactionType.REMOVAL:
        return "Removal"
    return "Transfer"


def _signed_amount_value(tx: Transaction) -> Decimal:
    if tx.type in (TransactionType.ADDITION, TransactionType.TRANSFER_IN):
        return tx.amount
    return -tx.amount


def format_history(rows: list[tuple[Transaction, Account]]) -> str:
    if not rows:
        return "No transactions."
    header = f"{'Date':<12}{'Account':<12}{'Type':<12}{'Amount':>12}{'Fee':>10}"
    lines = [header, "─" * len(header)]
    for tx, account in rows:
        day = _local_day(tx.timestamp)
        amount = _signed_amount_value(tx)
        fee_display = display_money(-tx.fee, width=10) if tx.fee > ZERO else f"{format_money(ZERO):>10}"
        lines.append(
            f"{day:<12}{account.name:<12}{_type_label(tx):<12}"
            f"{display_money(amount, signed=True, width=12)}{fee_display}"
        )
    return "\n".join(lines)


def format_balance_history(
    points: list[tuple[object, Decimal, Decimal | None]],
) -> str:
    if not points:
        return "No balance history yet."
    header = f"{'Date':<12}{'Total':>12}{'Change':>12}"
    lines = [header, "─" * len(header)]
    for when, total, change in points:
        day = _local_day(when)  # type: ignore[arg-type]
        if change is None:
            change_text = f"{'—':>12}"
        else:
            change_text = display_money(change, signed=True, width=12)
        lines.append(f"{day:<12}{display_money(total, width=12)}{change_text}")
    return "\n".join(lines)


def _format_period_block(stats: PeriodStats, *, title: str) -> list[str]:
    magnitudes = [stats.added, stats.removed, stats.fees, abs(stats.net_change)]
    maximum = max(magnitudes) if magnitudes else ZERO
    removed = -stats.removed
    fees = -stats.fees if stats.fees else ZERO

    lines = [
        title,
        f"  Added      {display_money(stats.added, signed=True, width=12)}  {_bar(stats.added, maximum)}",
        f"  Removed    {display_money(removed, signed=True, width=12)}  {_bar(removed, maximum)}",
        f"  Fees       {display_money(fees, signed=True, width=12) if stats.fees else display_money(ZERO, width=12)}  {_bar(fees, maximum)}",
        f"  Transfers  {display_money(stats.transfer_volume, width=12)}  {_bar(stats.transfer_volume, maximum, color=False)}",
        f"  Net change {display_money(stats.net_change, signed=True, width=12)}  {_bar(stats.net_change, maximum)}",
        "",
        f"  Starting   {display_money(stats.starting_balance, width=12)}",
        f"  Ending     {display_money(stats.ending_balance, width=12)}",
        f"  Change     {display_money(stats.ending_balance - stats.starting_balance, signed=True, width=12)}",
    ]
    return lines


def _format_savings_graphs(
    points: list[tuple[object, Decimal, Decimal | None]],
) -> list[str]:
    if not points:
        return [
            "Progression over time",
            "",
            *render_xy_chart([], title="Total savings"),
            "",
            *render_xy_chart([], title="Daily change"),
        ]

    # Keep recent history readable on a terminal.
    sample = points[-30:]
    totals = [
        (_local_day(when), total)  # type: ignore[arg-type]
        for when, total, _ in sample
    ]
    changes = [
        (_local_day(when), change if change is not None else ZERO)  # type: ignore[arg-type]
        for when, _, change in sample
    ]

    return [
        "Progression over time",
        "",
        *render_xy_chart(totals, title="Total savings"),
        "",
        *render_xy_chart(changes, title="Daily change"),
    ]


def format_stats(
    month: PeriodStats,
    all_time: PeriodStats,
    balance_points: list[tuple[object, Decimal, Decimal | None]] | None = None,
) -> str:
    lines = [
        f"Current savings  {display_money(all_time.ending_balance)}",
        "",
        *_format_period_block(month, title="This month"),
        "",
        *_format_period_block(all_time, title="All time"),
        "",
        *_format_savings_graphs(balance_points or []),
    ]
    return "\n".join(lines)


def format_goal(current: Decimal, goal: Decimal, progress: Decimal, remaining: Decimal) -> str:
    return "\n".join(
        [
            "Savings goal",
            "────────────────────────",
            f"Current       {display_money(current)}",
            f"Target        {display_money(goal)}",
            f"Progress        {progress}%",
            f"Remaining     {display_money(remaining)}",
        ]
    )


def format_snapshot(
    account: Account,
    ledger: Decimal,
    actual: Decimal,
) -> str:
    diff = actual - ledger
    return "\n".join(
        [
            account.name,
            "",
            f"Ledger balance:       {display_money(ledger)}",
            f"Actual balance:       {display_money(actual)}",
            f"Difference:           {display_money(diff, signed=True)}",
        ]
    )


def format_add_result(
    account: Account,
    amount: Decimal,
    fee: Decimal,
    new_balance: Decimal,
    parts: list[Decimal] | None = None,
) -> str:
    lines = [f"{account.name}: {display_money(amount, signed=True)}"]
    if parts and len(parts) > 1:
        breakdown = " + ".join(format_money(part) for part in parts)
        lines.append(f"Sum: {breakdown}")
    if fee > ZERO:
        lines.append(f"Fee: {display_money(-fee, signed=True)}")
        lines.append(f"Net: {display_money(amount - fee, signed=True)}")
    lines.append(f"Balance: {display_money(new_balance)}")
    return "\n".join(lines)


def format_remove_result(
    account: Account,
    amount: Decimal,
    fee: Decimal,
    new_balance: Decimal,
    parts: list[Decimal] | None = None,
) -> str:
    lines = [f"{account.name}: {display_money(-amount, signed=True)}"]
    if parts and len(parts) > 1:
        breakdown = " + ".join(format_money(part) for part in parts)
        lines.append(f"Sum: {breakdown}")
    if fee > ZERO:
        lines.append(f"Fee: {display_money(-fee, signed=True)}")
        lines.append(f"Net: {display_money(-(amount + fee), signed=True)}")
    lines.append(f"Balance: {display_money(new_balance)}")
    return "\n".join(lines)


def format_transfer_result(
    source: Account,
    destination: Account,
    amount: Decimal,
    fee: Decimal,
    source_balance: Decimal,
    dest_balance: Decimal,
) -> str:
    lines = [
        f"{source.name}: {display_money(-amount, signed=True)}",
        f"{destination.name}: {display_money(amount, signed=True)}",
    ]
    if fee > ZERO:
        lines.append(f"Fee ({destination.name}): {display_money(-fee, signed=True)}")
        lines.append(f"Net total: {display_money(-fee, signed=True)}")
    else:
        lines.append(f"Net total: {display_money(ZERO)}")
    lines.append(f"{source.name} balance: {display_money(source_balance)}")
    lines.append(f"{destination.name} balance: {display_money(dest_balance)}")
    return "\n".join(lines)
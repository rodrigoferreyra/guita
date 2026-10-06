"""CLI entrypoint (Typer). Presentation only — no financial calculations."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

from guita import __version__
from guita.app.service import GuitaService
from guita.cli import formatters
from guita.domain.errors import GuitaError, ValidationError
from guita.domain.money import looks_like_amount
from guita.persistence.db import default_db_path

_HELP_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _token_matches_known_account(token: str, known_accounts: list[str]) -> bool:
    """True if token is an exact or unique abbreviation of a known account."""
    folded = token.casefold()
    if any(name.casefold() == folded for name in known_accounts):
        return True
    if len(folded) < 3:
        return False
    matches = [name for name in known_accounts if name.casefold().startswith(folded)]
    return len(matches) == 1


def _split_amounts_and_account(
    values: list[str],
    *,
    known_accounts: list[str] | None = None,
) -> tuple[list[str], str]:
    """Split CLI tokens into amounts and one account name (order-independent)."""
    if len(values) < 2:
        raise ValidationError(
            "Error: provide one or more amounts and an account name.\n"
            "Examples: guita + 100 upwork\n"
            "          guita + upwork 100\n"
            "          guita + 42.5 297.5 upwork"
        )

    known = list(known_accounts or [])
    matched = [
        i for i, token in enumerate(values)
        if _token_matches_known_account(token, known)
    ]

    if len(matched) > 1:
        names = ", ".join(values[i] for i in matched)
        raise ValidationError(
            f"Error: multiple account names found in arguments: {names}.\n"
            "Provide exactly one account name."
        )

    if len(matched) == 1:
        account_index = matched[0]
    else:
        name_indexes = [i for i, token in enumerate(values) if not looks_like_amount(token)]
        if len(name_indexes) == 1:
            account_index = name_indexes[0]
        elif len(name_indexes) == 0:
            raise ValidationError(
                "Error: missing account name.\n"
                "Examples: guita + 100 upwork\n"
                "          guita + upwork 100"
            )
        else:
            names = ", ".join(values[i] for i in name_indexes)
            raise ValidationError(
                f"Error: could not determine the account name among: {names}.\n"
                "Provide exactly one account name with one or more amounts."
            )

    account = values[account_index]
    amounts = [values[i] for i in range(len(values)) if i != account_index]
    if not amounts:
        raise ValidationError(
            "Error: provide at least one amount with the account name.\n"
            "Examples: guita + 100 upwork\n"
            "          guita + upwork 100"
        )
    return amounts, account


app = typer.Typer(
    name="guita",
    help="Local-first CLI for tracking personal savings.",
    no_args_is_help=False,
    invoke_without_command=True,
    add_completion=False,
    context_settings=_HELP_SETTINGS,
)

account_app = typer.Typer(
    help="Manage accounts.",
    add_completion=False,
    context_settings=_HELP_SETTINGS,
)
app.add_typer(account_app, name="account")


def _service() -> GuitaService:
    return GuitaService()


def _fail(exc: GuitaError) -> None:
    typer.echo(exc.message, err=True)
    raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """Show balances when no subcommand is given."""
    if ctx.invoked_subcommand is None:
        balance()


@app.command("balance")
def balance() -> None:
    """Show current account balances."""
    try:
        with _service() as svc:
            items = svc.balances()
            typer.echo(formatters.format_balances(items, svc.total_balance()))
    except GuitaError as exc:
        _fail(exc)


def _add_money_command(
    values: list[str],
    fee: Optional[str],
) -> None:
    try:
        with _service() as svc:
            known = [account.name for account in svc.list_accounts()]
            amounts, account = _split_amounts_and_account(
                values, known_accounts=known
            )
            tx, parts = svc.add_money(amounts, account, fee=fee)
            acct = next(a.account for a in svc.balances() if a.account.id == tx.account_id)
            typer.echo(
                formatters.format_add_result(
                    acct, tx.amount, tx.fee, svc.account_balance(acct), parts=parts
                )
            )
    except GuitaError as exc:
        _fail(exc)


def _remove_money_command(
    values: list[str],
    fee: Optional[str],
) -> None:
    try:
        with _service() as svc:
            known = [account.name for account in svc.list_accounts()]
            amounts, account = _split_amounts_and_account(
                values, known_accounts=known
            )
            tx, parts = svc.remove_money(amounts, account, fee=fee)
            acct = next(a.account for a in svc.balances() if a.account.id == tx.account_id)
            typer.echo(
                formatters.format_remove_result(
                    acct, tx.amount, tx.fee, svc.account_balance(acct), parts=parts
                )
            )
    except GuitaError as exc:
        _fail(exc)


@app.command("+")
@app.command("add")
def add_money(
    values: list[str] = typer.Argument(
        ...,
        help="Account name and one or more amounts, in any order.",
    ),
    fee: Optional[str] = typer.Option(None, "--fee", help="Optional fee."),
) -> None:
    """Add money to an account. Multiple amounts are summed."""
    _add_money_command(values, fee)


@app.command("-")
@app.command("remove")
def remove_money(
    values: list[str] = typer.Argument(
        ...,
        help="Account name and one or more amounts, in any order.",
    ),
    fee: Optional[str] = typer.Option(None, "--fee", help="Optional fee."),
) -> None:
    """Remove money from an account. Multiple amounts are summed."""
    _remove_money_command(values, fee)


@app.command("set")
def set_balance(
    account: str = typer.Argument(..., help="Account name."),
    balance_value: str = typer.Argument(..., help="Target ledger balance."),
) -> None:
    """Set an account balance by recording a corrective addition or removal."""
    try:
        with _service() as svc:
            acct, previous, target, tx = svc.set_balance(account, balance_value)
            adjustment = None if tx is None else (
                tx.amount if tx.type.value == "addition" else -tx.amount
            )
            typer.echo(
                formatters.format_set_result(acct, previous, target, adjustment)
            )
    except GuitaError as exc:
        _fail(exc)


@app.command("transfer")
def transfer(
    amount: str = typer.Argument(..., help="Positive amount to transfer."),
    source: str = typer.Argument(..., help="Sender account."),
    destination: str = typer.Argument(..., help="Recipient account."),
    fee: Optional[str] = typer.Option(
        None, "--fee", help="Optional fee paid by the destination account."
    ),
) -> None:
    """Transfer money from source to destination."""
    try:
        with _service() as svc:
            result = svc.transfer(amount, source, destination, fee=fee)
            src = svc.get_account(source)
            dst = svc.get_account(destination)
            typer.echo(
                formatters.format_transfer_result(
                    src,
                    dst,
                    result.amount,
                    result.fee,
                    svc.account_balance(src),
                    svc.account_balance(dst),
                )
            )
    except GuitaError as exc:
        _fail(exc)


@app.command("history")
def history(
    account: Optional[str] = typer.Option(None, "--account", help="Filter by account."),
    from_date: Optional[str] = typer.Option(None, "--from", help="Start date YYYY-MM-DD."),
    to_date: Optional[str] = typer.Option(None, "--to", help="End date YYYY-MM-DD."),
    tx_type: Optional[str] = typer.Option(None, "--type", help="addition|removal|transfer"),
    balances: bool = typer.Option(False, "--balances", help="Show historical totals."),
) -> None:
    """Show transaction history."""
    try:
        with _service() as svc:
            if balances:
                typer.echo(formatters.format_balance_history(svc.balance_history()))
                return
            rows = svc.history(
                account_name=account,
                from_date=from_date,
                to_date=to_date,
                tx_type=tx_type,
            )
            typer.echo(formatters.format_history(rows))
    except GuitaError as exc:
        _fail(exc)


@app.command("snapshot")
def snapshot(
    account: str = typer.Argument(..., help="Account name."),
    balance_value: str = typer.Argument(..., help="Observed actual balance."),
) -> None:
    """Record an observed real-world account balance."""
    try:
        with _service() as svc:
            snap, ledger = svc.snapshot(account, balance_value)
            acct = svc.get_account(account)
            typer.echo(formatters.format_snapshot(acct, ledger, snap.balance))
    except GuitaError as exc:
        _fail(exc)


@app.command("stats")
def stats() -> None:
    """Show this-month and all-time savings statistics with simple graphs."""
    try:
        with _service() as svc:
            typer.echo(
                formatters.format_stats(
                    svc.stats(),
                    svc.stats(all_time=True),
                    svc.balance_history(),
                )
            )
    except GuitaError as exc:
        _fail(exc)


@app.command("goal")
def goal(
    amount: Optional[str] = typer.Argument(
        None, help="Set a savings goal. Omit to show current progress."
    ),
) -> None:
    """Set or show the savings goal."""
    try:
        with _service() as svc:
            if amount is not None:
                svc.set_goal(amount)
            progress = svc.goal_progress()
            if progress is None:
                typer.echo("No savings goal set. Use: guita goal <amount>")
                return
            current, target, pct, remaining = progress
            typer.echo(formatters.format_goal(current, target, pct, remaining))
    except GuitaError as exc:
        _fail(exc)


@app.command("export")
def export(
    path: Path = typer.Argument(
        Path("transactions.csv"),
        help="Output file (.csv or .json).",
    ),
) -> None:
    """Export the transaction ledger."""
    try:
        with _service() as svc:
            out = svc.export_transactions(path)
            typer.echo(f"Exported to {out}")
    except GuitaError as exc:
        _fail(exc)


@app.command("backup")
def backup(
    path: Optional[Path] = typer.Argument(None, help="Optional backup destination."),
) -> None:
    """Copy the database file to a backup location."""
    try:
        with _service() as svc:
            out = svc.backup(path)
            typer.echo(f"Backup written to {out}")
    except GuitaError as exc:
        _fail(exc)


@app.command("info")
def info() -> None:
    """Show version and database location."""
    db = default_db_path()
    typer.echo("Guita")
    typer.echo(f"Version: {__version__}")
    typer.echo(f"Database: {db}")


@account_app.command("add")
def account_add(
    name: str = typer.Argument(..., help="Account name."),
    currency: str = typer.Argument("USD", help="Currency (USD only for now)."),
    alias: Optional[str] = typer.Option(
        None,
        "--alias",
        "-a",
        help="Unique alias when the default 3-letter short code would overlap.",
    ),
) -> None:
    """Create an account."""
    try:
        with _service() as svc:
            account = svc.add_account(name, currency, alias=alias)
            if account.alias:
                typer.echo(
                    f"Created {account.name} — {account.currency} "
                    f"(alias: {account.alias})"
                )
            else:
                typer.echo(f"Created {account.name} — {account.currency}")
    except GuitaError as exc:
        _fail(exc)


@account_app.command("alias")
def account_set_alias(
    name: str = typer.Argument(..., help="Account name or current reference."),
    alias: str = typer.Argument(..., help="Unique alias (at least 3 characters)."),
) -> None:
    """Assign a unique alias used as a short reference for an account."""
    try:
        with _service() as svc:
            account = svc.set_alias(name, alias)
            typer.echo(f"Alias for {account.name}: {account.alias}")
    except GuitaError as exc:
        _fail(exc)


@account_app.command("list")
def account_list() -> None:
    """List accounts."""
    try:
        with _service() as svc:
            typer.echo(formatters.format_accounts(svc.list_accounts()))
    except GuitaError as exc:
        _fail(exc)


@account_app.command("deactivate")
def account_deactivate(
    name: str = typer.Argument(..., help="Account name."),
) -> None:
    """Deactivate an account (blocks new transactions)."""
    try:
        with _service() as svc:
            account = svc.deactivate_account(name)
            typer.echo(f"Deactivated {account.name}")
    except GuitaError as exc:
        _fail(exc)


def main() -> None:
    try:
        app()
    except typer.Exit:
        raise
    except GuitaError as exc:
        print(exc.message, file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
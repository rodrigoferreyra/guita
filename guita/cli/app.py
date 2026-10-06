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
from guita.persistence.db import default_db_path

_HELP_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _split_amounts_and_account(values: list[str]) -> tuple[list[str], str]:
    """Last token is the account; preceding tokens are amounts to sum."""
    if len(values) < 2:
        raise ValidationError(
            "Error: provide one or more amounts followed by an account name.\n"
            "Example: guita + 42.5 297.5 upwork"
        )
    return values[:-1], values[-1]

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


@app.command("+")
def add_money(
    values: list[str] = typer.Argument(
        ...,
        help="One or more amounts, then the account name.",
    ),
    fee: Optional[str] = typer.Option(None, "--fee", help="Optional fee."),
) -> None:
    """Add money to an account. Multiple amounts are summed."""
    try:
        amounts, account = _split_amounts_and_account(values)
        with _service() as svc:
            tx, parts = svc.add_money(amounts, account, fee=fee)
            acct = next(a.account for a in svc.balances() if a.account.id == tx.account_id)
            typer.echo(
                formatters.format_add_result(
                    acct, tx.amount, tx.fee, svc.account_balance(acct), parts=parts
                )
            )
    except GuitaError as exc:
        _fail(exc)


@app.command("-")
def remove_money(
    values: list[str] = typer.Argument(
        ...,
        help="One or more amounts, then the account name.",
    ),
    fee: Optional[str] = typer.Option(None, "--fee", help="Optional fee."),
) -> None:
    """Remove money from an account. Multiple amounts are summed."""
    try:
        amounts, account = _split_amounts_and_account(values)
        with _service() as svc:
            tx, parts = svc.remove_money(amounts, account, fee=fee)
            acct = next(a.account for a in svc.balances() if a.account.id == tx.account_id)
            typer.echo(
                formatters.format_remove_result(
                    acct, tx.amount, tx.fee, svc.account_balance(acct), parts=parts
                )
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
) -> None:
    """Create an account."""
    try:
        with _service() as svc:
            account = svc.add_account(name, currency)
            typer.echo(f"Created {account.name} — {account.currency}")
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
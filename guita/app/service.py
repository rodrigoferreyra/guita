"""Application services: orchestrate domain rules and persistence."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from guita.domain.errors import (
    ConflictError,
    InsufficientBalanceError,
    NotFoundError,
    ValidationError,
)
from guita.domain.ledger import balance_for_account, total_savings, transaction_delta
from guita.domain.money import (
    ZERO,
    format_money,
    parse_money,
    parse_non_negative_fee,
    parse_positive_amount,
    sum_positive_amounts,
)
from guita.domain.models import (
    Account,
    AccountBalance,
    Snapshot,
    Transaction,
    TransactionType,
    Transfer,
)
from guita.persistence.db import connect, default_db_path, initialize_db
from guita.persistence.repository import Repository


SUPPORTED_CURRENCY = "USD"


@dataclass(frozen=True)
class PeriodStats:
    added: Decimal
    removed: Decimal
    fees: Decimal
    transfer_volume: Decimal
    net_change: Decimal
    starting_balance: Decimal
    ending_balance: Decimal


class GuitaService:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path if db_path is not None else default_db_path()
        self._conn = connect(self.db_path)
        initialize_db(self._conn)
        self._repo = Repository(self._conn)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> GuitaService:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # --- accounts ---

    def add_account(self, name: str, currency: str = SUPPORTED_CURRENCY) -> Account:
        cleaned = name.strip()
        if not cleaned:
            raise ValidationError("Error: account name must not be empty.")
        currency = currency.strip().upper()
        if currency != SUPPORTED_CURRENCY:
            raise ValidationError(
                f'Error: currency "{currency}" is not supported. '
                f"Only {SUPPORTED_CURRENCY} is supported."
            )
        existing = self._repo.get_account_by_name(cleaned)
        if existing is not None:
            raise ConflictError(
                f'Error: account "{existing.name}" already exists.'
            )
        return self._repo.create_account(cleaned, currency)

    def list_accounts(self) -> list[Account]:
        return self._repo.list_accounts()

    def get_account(self, name: str) -> Account:
        return self._require_account(name)

    def deactivate_account(self, name: str) -> Account:
        account = self._require_account(name)
        if not account.active:
            raise ConflictError(f'Error: account "{account.name}" is already inactive.')
        self._repo.set_account_active(account.id, False)
        updated = self._repo.get_account(account.id)
        assert updated is not None
        return updated

    # --- balances ---

    def account_balance(self, account: Account) -> Decimal:
        txs = self._repo.transactions_for_account(account.id)
        return balance_for_account(txs, account.id)

    def balances(self) -> list[AccountBalance]:
        accounts = self._repo.list_accounts(active_only=False)
        result: list[AccountBalance] = []
        for account in accounts:
            result.append(
                AccountBalance(account=account, balance=self.account_balance(account))
            )
        return result

    def total_balance(self) -> Decimal:
        return total_savings(self._repo.all_transactions())

    # --- mutations ---

    def add_money(
        self,
        amount: str | Decimal | list[str | Decimal],
        account_name: str,
        fee: str | Decimal | None = None,
    ) -> tuple[Transaction, list[Decimal]]:
        account = self._require_active_account(account_name)
        value, parts = sum_positive_amounts(amount)
        fee_value = parse_non_negative_fee(fee)
        # Addition with fee: net = amount - fee. Reject if resulting balance < 0.
        current = self.account_balance(account)
        projected = current + value - fee_value
        if projected < ZERO:
            raise InsufficientBalanceError(
                f"Error: {account.name} balance is {format_money(current)}. "
                f"This addition with fee would leave "
                f"{format_money(projected)}."
            )
        tx = self._repo.add_transaction(
            type=TransactionType.ADDITION,
            account_id=account.id,
            amount=value,
            fee=fee_value,
        )
        return tx, parts

    def remove_money(
        self,
        amount: str | Decimal | list[str | Decimal],
        account_name: str,
        fee: str | Decimal | None = None,
    ) -> tuple[Transaction, list[Decimal]]:
        account = self._require_active_account(account_name)
        value, parts = sum_positive_amounts(amount)
        fee_value = parse_non_negative_fee(fee)
        current = self.account_balance(account)
        needed = value + fee_value
        if current < needed:
            raise InsufficientBalanceError(
                f"Error: {account.name} balance is {format_money(current)}. "
                f"You cannot remove {format_money(value)}"
                + (
                    f" with fee {format_money(fee_value)}"
                    if fee_value > ZERO
                    else ""
                )
                + "."
            )
        tx = self._repo.add_transaction(
            type=TransactionType.REMOVAL,
            account_id=account.id,
            amount=value,
            fee=fee_value,
        )
        return tx, parts

    def transfer(
        self,
        amount: str | Decimal,
        source_name: str,
        destination_name: str,
        fee: str | Decimal | None = None,
    ) -> Transfer:
        source = self._require_active_account(source_name)
        destination = self._require_active_account(destination_name)
        if source.id == destination.id:
            raise ValidationError(
                "Error: source and destination accounts must be different."
            )
        value = parse_positive_amount(amount)
        fee_value = parse_non_negative_fee(fee)

        source_balance = self.account_balance(source)
        if source_balance < value:
            raise InsufficientBalanceError(
                f"Error: {source.name} balance is {format_money(source_balance)}. "
                f"You cannot transfer {format_money(value)}."
            )

        # Destination pays the fee: receives amount, then fee reduces its balance.
        dest_balance = self.account_balance(destination)
        dest_projected = dest_balance + value - fee_value
        if dest_projected < ZERO:
            raise InsufficientBalanceError(
                f"Error: {destination.name} balance is {format_money(dest_balance)}. "
                f"Receiving {format_money(value)} with fee {format_money(fee_value)} "
                f"would leave {format_money(dest_projected)}."
            )

        return self._repo.create_transfer(
            source_account_id=source.id,
            destination_account_id=destination.id,
            amount=value,
            fee=fee_value,
        )

    # --- history ---

    def history(
        self,
        *,
        account_name: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        tx_type: str | None = None,
    ) -> list[tuple[Transaction, Account]]:
        account_id = None
        if account_name is not None:
            account_id = self._require_account(account_name).id

        types = None
        if tx_type is not None:
            types = self._parse_type_filter(tx_type)

        from_ts = self._parse_date_start(from_date) if from_date else None
        to_ts = self._parse_date_end(to_date) if to_date else None

        accounts = {a.id: a for a in self._repo.list_accounts()}
        txs = self._repo.list_transactions(
            account_id=account_id,
            types=types,
            from_ts=from_ts,
            to_ts=to_ts,
        )
        return [(tx, accounts[tx.account_id]) for tx in txs]

    def balance_history(self) -> list[tuple[datetime, Decimal, Decimal | None]]:
        """Return (date, total, change_from_previous) at each transaction timestamp."""
        txs = self._repo.all_transactions()
        if not txs:
            return []

        running = ZERO
        # Group by local calendar date so charts match the user's day.
        by_date: dict[str, Decimal] = {}
        for tx in txs:
            running += transaction_delta(tx)
            day = tx.timestamp.astimezone().date().isoformat()
            by_date[day] = running

        previous: Decimal | None = None
        points: list[tuple[datetime, Decimal, Decimal | None]] = []
        for day in sorted(by_date):
            total = by_date[day]
            change = None if previous is None else total - previous
            # Naive datetime representing a calendar day (not a UTC instant).
            points.append((datetime.fromisoformat(day), total, change))
            previous = total
        return points

    # --- snapshots ---

    def snapshot(self, account_name: str, balance: str | Decimal) -> tuple[Snapshot, Decimal]:
        account = self._require_account(account_name)
        actual = parse_money(balance, field="balance")
        if actual < ZERO:
            raise ValidationError("Error: snapshot balance must be greater than or equal to zero.")
        snap = self._repo.add_snapshot(account.id, actual)
        ledger = self.account_balance(account)
        return snap, ledger

    def reconciliation(self, account_name: str) -> tuple[Account, Decimal, Decimal | None, Decimal | None]:
        account = self._require_account(account_name)
        ledger = self.account_balance(account)
        snap = self._repo.latest_snapshot(account.id)
        if snap is None:
            return account, ledger, None, None
        return account, ledger, snap.balance, snap.balance - ledger

    # --- stats ---

    def stats(
        self,
        *,
        all_time: bool = False,
        year: int | None = None,
        month: int | None = None,
    ) -> PeriodStats:
        txs = self._repo.all_transactions()
        now = datetime.now(timezone.utc)

        if all_time:
            start = datetime(1970, 1, 1, tzinfo=timezone.utc)
            end = datetime(9999, 1, 1, tzinfo=timezone.utc)
        elif year is None and month is None:
            year = now.year
            month = now.month
            start = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        elif month is not None:
            assert year is not None
            start = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        elif year is not None:
            start = datetime(year, 1, 1, tzinfo=timezone.utc)
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            start = datetime(1970, 1, 1, tzinfo=timezone.utc)
            end = datetime(9999, 1, 1, tzinfo=timezone.utc)

        starting = ZERO
        added = ZERO
        removed = ZERO
        fees = ZERO
        transfer_volume = ZERO
        ending = ZERO

        for tx in txs:
            ts = tx.timestamp.astimezone(timezone.utc)
            delta = transaction_delta(tx)
            if ts < start:
                starting += delta
            if ts < end:
                ending += delta
            if start <= ts < end:
                fees += tx.fee
                if tx.type is TransactionType.ADDITION:
                    added += tx.amount
                elif tx.type is TransactionType.REMOVAL:
                    removed += tx.amount
                elif tx.type is TransactionType.TRANSFER_OUT:
                    transfer_volume += tx.amount

        # Net savings change excludes transfer principal; fees always reduce savings.
        net = added - removed - fees
        return PeriodStats(
            added=added,
            removed=removed,
            fees=fees,
            transfer_volume=transfer_volume,
            net_change=net,
            starting_balance=starting,
            ending_balance=ending,
        )

    # --- goal ---

    def set_goal(self, amount: str | Decimal) -> Decimal:
        value = parse_positive_amount(amount, field="goal")
        self._repo.set_setting("savings_goal", format(value, "f"))
        return value

    def get_goal(self) -> Decimal | None:
        raw = self._repo.get_setting("savings_goal")
        if raw is None:
            return None
        return Decimal(raw)

    def goal_progress(self) -> tuple[Decimal, Decimal, Decimal, Decimal] | None:
        goal = self.get_goal()
        if goal is None:
            return None
        current = self.total_balance()
        remaining = max(goal - current, ZERO)
        progress = (current / goal * Decimal("100")).quantize(Decimal("0.1")) if goal else ZERO
        return current, goal, progress, remaining

    # --- export / backup ---

    def export_transactions(self, path: Path) -> Path:
        path = path.expanduser()
        rows = self.history()
        if path.suffix.lower() == ".json":
            payload = []
            for tx, account in rows:
                payload.append(
                    {
                        "id": tx.id,
                        "timestamp": tx.timestamp.isoformat(),
                        "account": account.name,
                        "type": tx.type.value,
                        "amount": format(tx.amount, "f"),
                        "fee": format(tx.fee, "f"),
                        "transfer_id": tx.transfer_id,
                        "description": tx.description,
                    }
                )
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        else:
            # default CSV
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(
                    [
                        "id",
                        "timestamp",
                        "account",
                        "type",
                        "amount",
                        "fee",
                        "transfer_id",
                        "description",
                    ]
                )
                for tx, account in rows:
                    writer.writerow(
                        [
                            tx.id,
                            tx.timestamp.isoformat(),
                            account.name,
                            tx.type.value,
                            format(tx.amount, "f"),
                            format(tx.fee, "f"),
                            tx.transfer_id or "",
                            tx.description or "",
                        ]
                    )
        return path

    def backup(self, path: Path | None = None) -> Path:
        if path is None:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            path = self.db_path.parent / f"guita-backup-{stamp}.db"
        else:
            path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn.commit()
        shutil.copy2(self.db_path, path)
        return path

    # --- helpers ---

    def _require_account(self, name: str) -> Account:
        account = self._repo.get_account_by_name(name)
        if account is None:
            available = ", ".join(a.name for a in self._repo.list_accounts()) or "(none)"
            raise NotFoundError(
                f'Error: account "{name}" does not exist.\n'
                f"Available accounts: {available}"
            )
        return account

    def _require_active_account(self, name: str) -> Account:
        account = self._require_account(name)
        if not account.active:
            raise ConflictError(
                f'Error: account "{account.name}" is inactive. '
                "Reactivate it before recording transactions."
            )
        return account

    @staticmethod
    def _parse_type_filter(value: str) -> list[TransactionType]:
        key = value.strip().lower()
        mapping = {
            "addition": [TransactionType.ADDITION],
            "add": [TransactionType.ADDITION],
            "removal": [TransactionType.REMOVAL],
            "remove": [TransactionType.REMOVAL],
            "transfer": [TransactionType.TRANSFER_OUT, TransactionType.TRANSFER_IN],
        }
        if key not in mapping:
            raise ValidationError(
                f'Error: unknown transaction type "{value}". '
                "Use addition, removal, or transfer."
            )
        return mapping[key]

    @staticmethod
    def _parse_date_start(value: str) -> datetime:
        try:
            day = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError(
                f'Error: date "{value}" is invalid. Use YYYY-MM-DD.'
            ) from exc
        return datetime(day.year, day.month, day.day, tzinfo=timezone.utc)

    @staticmethod
    def _parse_date_end(value: str) -> datetime:
        try:
            day = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError(
                f'Error: date "{value}" is invalid. Use YYYY-MM-DD.'
            ) from exc
        return datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)
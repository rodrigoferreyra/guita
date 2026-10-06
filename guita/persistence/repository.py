"""SQLite persistence for accounts, transactions, transfers, snapshots."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from decimal import Decimal

from guita.domain.models import (
    Account,
    Snapshot,
    Transaction,
    TransactionType,
    Transfer,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _dt_to_str(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _str_to_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _money_to_str(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _str_to_money(value: str) -> Decimal:
    return Decimal(value)


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # --- accounts ---

    def create_account(
        self,
        name: str,
        currency: str = "USD",
        alias: str | None = None,
    ) -> Account:
        created_at = _utcnow()
        cur = self._conn.execute(
            """
            INSERT INTO accounts (name, currency, created_at, active, alias)
            VALUES (?, ?, ?, 1, ?)
            """,
            (name, currency, _dt_to_str(created_at), alias),
        )
        self._conn.commit()
        return Account(
            id=int(cur.lastrowid),
            name=name,
            currency=currency,
            created_at=created_at,
            active=True,
            alias=alias,
        )

    def list_accounts(self, *, active_only: bool = False) -> list[Account]:
        if active_only:
            rows = self._conn.execute(
                "SELECT * FROM accounts WHERE active = 1 ORDER BY name COLLATE NOCASE"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM accounts ORDER BY name COLLATE NOCASE"
            ).fetchall()
        return [self._account_from_row(r) for r in rows]

    def get_account_by_name(self, name: str) -> Account | None:
        row = self._conn.execute(
            "SELECT * FROM accounts WHERE lower(name) = lower(?)",
            (name,),
        ).fetchone()
        return self._account_from_row(row) if row else None

    def get_account_by_alias(self, alias: str) -> Account | None:
        row = self._conn.execute(
            "SELECT * FROM accounts WHERE alias IS NOT NULL AND lower(alias) = lower(?)",
            (alias,),
        ).fetchone()
        return self._account_from_row(row) if row else None

    def get_account(self, account_id: int) -> Account | None:
        row = self._conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        return self._account_from_row(row) if row else None

    def set_account_active(self, account_id: int, active: bool) -> None:
        self._conn.execute(
            "UPDATE accounts SET active = ? WHERE id = ?",
            (1 if active else 0, account_id),
        )
        self._conn.commit()

    def set_account_alias(self, account_id: int, alias: str | None) -> None:
        self._conn.execute(
            "UPDATE accounts SET alias = ? WHERE id = ?",
            (alias, account_id),
        )
        self._conn.commit()

    # --- transactions ---

    def add_transaction(
        self,
        *,
        type: TransactionType,
        account_id: int,
        amount: Decimal,
        fee: Decimal = Decimal("0.00"),
        transfer_id: int | None = None,
        description: str | None = None,
        timestamp: datetime | None = None,
        commit: bool = True,
    ) -> Transaction:
        ts = timestamp or _utcnow()
        cur = self._conn.execute(
            """
            INSERT INTO transactions
                (timestamp, type, account_id, amount, fee, transfer_id, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _dt_to_str(ts),
                type.value,
                account_id,
                _money_to_str(amount),
                _money_to_str(fee),
                transfer_id,
                description,
            ),
        )
        if commit:
            self._conn.commit()
        return Transaction(
            id=int(cur.lastrowid),
            timestamp=ts,
            type=type,
            account_id=account_id,
            amount=amount.quantize(Decimal("0.01")),
            fee=fee.quantize(Decimal("0.01")),
            transfer_id=transfer_id,
            description=description,
        )

    def list_transactions(
        self,
        *,
        account_id: int | None = None,
        types: list[TransactionType] | None = None,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
    ) -> list[Transaction]:
        clauses: list[str] = []
        params: list[object] = []
        if account_id is not None:
            clauses.append("account_id = ?")
            params.append(account_id)
        if types:
            placeholders = ", ".join("?" for _ in types)
            clauses.append(f"type IN ({placeholders})")
            params.extend(t.value for t in types)
        if from_ts is not None:
            clauses.append("timestamp >= ?")
            params.append(_dt_to_str(from_ts))
        if to_ts is not None:
            clauses.append("timestamp <= ?")
            params.append(_dt_to_str(to_ts))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._conn.execute(
            f"""
            SELECT * FROM transactions
            {where}
            ORDER BY timestamp ASC, id ASC
            """,
            params,
        ).fetchall()
        return [self._transaction_from_row(r) for r in rows]

    def transactions_for_account(self, account_id: int) -> list[Transaction]:
        return self.list_transactions(account_id=account_id)

    def all_transactions(self) -> list[Transaction]:
        return self.list_transactions()

    # --- transfers ---

    def create_transfer(
        self,
        *,
        source_account_id: int,
        destination_account_id: int,
        amount: Decimal,
        fee: Decimal,
        description: str | None = None,
        timestamp: datetime | None = None,
    ) -> Transfer:
        ts = timestamp or _utcnow()
        try:
            cur = self._conn.execute(
                """
                INSERT INTO transfers
                    (timestamp, source_account_id, destination_account_id,
                     amount, fee, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    _dt_to_str(ts),
                    source_account_id,
                    destination_account_id,
                    _money_to_str(amount),
                    _money_to_str(fee),
                    description,
                ),
            )
            transfer_id = int(cur.lastrowid)
            self.add_transaction(
                type=TransactionType.TRANSFER_OUT,
                account_id=source_account_id,
                amount=amount,
                fee=Decimal("0.00"),
                transfer_id=transfer_id,
                description=description,
                timestamp=ts,
                commit=False,
            )
            self.add_transaction(
                type=TransactionType.TRANSFER_IN,
                account_id=destination_account_id,
                amount=amount,
                fee=fee,
                transfer_id=transfer_id,
                description=description,
                timestamp=ts,
                commit=False,
            )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

        return Transfer(
            id=transfer_id,
            timestamp=ts,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=amount.quantize(Decimal("0.01")),
            fee=fee.quantize(Decimal("0.01")),
            description=description,
        )

    # --- snapshots ---

    def add_snapshot(
        self,
        account_id: int,
        balance: Decimal,
        timestamp: datetime | None = None,
    ) -> Snapshot:
        ts = timestamp or _utcnow()
        cur = self._conn.execute(
            """
            INSERT INTO snapshots (timestamp, account_id, balance)
            VALUES (?, ?, ?)
            """,
            (_dt_to_str(ts), account_id, _money_to_str(balance)),
        )
        self._conn.commit()
        return Snapshot(
            id=int(cur.lastrowid),
            timestamp=ts,
            account_id=account_id,
            balance=balance.quantize(Decimal("0.01")),
        )

    def latest_snapshot(self, account_id: int) -> Snapshot | None:
        row = self._conn.execute(
            """
            SELECT * FROM snapshots
            WHERE account_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
            """,
            (account_id,),
        ).fetchone()
        return self._snapshot_from_row(row) if row else None

    # --- settings ---

    def get_setting(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        ).fetchone()
        return str(row["value"]) if row else None

    def set_setting(self, key: str, value: str) -> None:
        self._conn.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        self._conn.commit()

    # --- mappers ---

    @staticmethod
    def _account_from_row(row: sqlite3.Row) -> Account:
        alias = row["alias"] if "alias" in row.keys() else None
        return Account(
            id=int(row["id"]),
            name=str(row["name"]),
            currency=str(row["currency"]),
            created_at=_str_to_dt(str(row["created_at"])),
            active=bool(row["active"]),
            alias=str(alias) if alias is not None else None,
        )

    @staticmethod
    def _transaction_from_row(row: sqlite3.Row) -> Transaction:
        transfer_id = row["transfer_id"]
        return Transaction(
            id=int(row["id"]),
            timestamp=_str_to_dt(str(row["timestamp"])),
            type=TransactionType(str(row["type"])),
            account_id=int(row["account_id"]),
            amount=_str_to_money(str(row["amount"])),
            fee=_str_to_money(str(row["fee"])),
            transfer_id=int(transfer_id) if transfer_id is not None else None,
            description=row["description"],
        )

    @staticmethod
    def _snapshot_from_row(row: sqlite3.Row) -> Snapshot:
        return Snapshot(
            id=int(row["id"]),
            timestamp=_str_to_dt(str(row["timestamp"])),
            account_id=int(row["account_id"]),
            balance=_str_to_money(str(row["balance"])),
        )
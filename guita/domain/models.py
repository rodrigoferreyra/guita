"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    ADDITION = "addition"
    REMOVAL = "removal"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"


@dataclass(frozen=True)
class Account:
    id: int
    name: str
    currency: str
    created_at: datetime
    active: bool
    alias: str | None = None


@dataclass(frozen=True)
class Transaction:
    id: int
    timestamp: datetime
    type: TransactionType
    account_id: int
    amount: Decimal
    fee: Decimal
    transfer_id: int | None
    description: str | None


@dataclass(frozen=True)
class Transfer:
    id: int
    timestamp: datetime
    source_account_id: int
    destination_account_id: int
    amount: Decimal
    fee: Decimal
    description: str | None


@dataclass(frozen=True)
class Snapshot:
    id: int
    timestamp: datetime
    account_id: int
    balance: Decimal


@dataclass(frozen=True)
class AccountBalance:
    account: Account
    balance: Decimal


@dataclass(frozen=True)
class LedgerEffect:
    """Net change applied to one account by a recorded operation."""

    account_id: int
    delta: Decimal
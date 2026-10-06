"""Pure ledger rules and balance calculations."""

from __future__ import annotations

from decimal import Decimal

from guita.domain.money import ZERO
from guita.domain.models import Transaction, TransactionType


def transaction_delta(tx: Transaction) -> Decimal:
    """Net balance change for the account owning this transaction row."""
    if tx.type is TransactionType.ADDITION:
        return tx.amount - tx.fee
    if tx.type is TransactionType.REMOVAL:
        return -(tx.amount + tx.fee)
    if tx.type is TransactionType.TRANSFER_OUT:
        return -tx.amount
    if tx.type is TransactionType.TRANSFER_IN:
        return tx.amount - tx.fee
    raise ValueError(f"Unknown transaction type: {tx.type}")


def balance_for_account(transactions: list[Transaction], account_id: int) -> Decimal:
    total = ZERO
    for tx in transactions:
        if tx.account_id == account_id:
            total += transaction_delta(tx)
    return total


def total_savings(transactions: list[Transaction]) -> Decimal:
    total = ZERO
    for tx in transactions:
        total += transaction_delta(tx)
    return total
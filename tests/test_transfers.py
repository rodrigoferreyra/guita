"""Transfers and destination-paid fees."""

from decimal import Decimal

import pytest

from guita.app.service import GuitaService
from guita.domain.errors import InsufficientBalanceError, ValidationError
from guita.domain.models import TransactionType


def test_transfer(funded: GuitaService) -> None:
    funded.transfer("400", "Wise", "Wallbit")
    assert funded.account_balance(funded.get_account("Wise")) == Decimal("600.00")
    assert funded.account_balance(funded.get_account("Wallbit")) == Decimal("400.00")
    assert funded.total_balance() == Decimal("1000.00")


def test_transfer_with_fee_paid_by_destination(funded: GuitaService) -> None:
    funded.transfer("400", "Wise", "Wallbit", fee="5")
    assert funded.account_balance(funded.get_account("Wise")) == Decimal("600.00")
    assert funded.account_balance(funded.get_account("Wallbit")) == Decimal("395.00")
    assert funded.total_balance() == Decimal("995.00")


def test_transfer_cli_argument_order(funded: GuitaService) -> None:
    """First account is sender, second is recipient."""
    funded.transfer("100", "wise", "wallbit")
    assert funded.account_balance(funded.get_account("Wise")) == Decimal("900.00")
    assert funded.account_balance(funded.get_account("Wallbit")) == Decimal("100.00")


def test_same_account_transfer_rejected(funded: GuitaService) -> None:
    with pytest.raises(ValidationError, match="different"):
        funded.transfer("10", "Wise", "Wise")


def test_insufficient_source_balance(funded: GuitaService) -> None:
    with pytest.raises(InsufficientBalanceError):
        funded.transfer("2000", "Wise", "Wallbit")


def test_fee_cannot_drive_destination_negative(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_account("Wallbit", "USD")
    svc.add_money("10", "Wise")
    # Dest starts at 0; receive 10 with fee 15 → -5
    with pytest.raises(InsufficientBalanceError, match="Wallbit"):
        svc.transfer("10", "Wise", "Wallbit", fee="15")


def test_transfer_history_marks_both_legs(funded: GuitaService) -> None:
    funded.transfer("500", "Wise", "Wallbit", fee="5")
    rows = funded.history()
    types = [tx.type for tx, _ in rows if tx.transfer_id is not None]
    assert TransactionType.TRANSFER_OUT in types
    assert TransactionType.TRANSFER_IN in types
    dest_leg = next(
        tx for tx, acct in rows if acct.name == "Wallbit" and tx.transfer_id is not None
    )
    assert dest_leg.fee == Decimal("5.00")
    assert dest_leg.amount == Decimal("500.00")


def test_transfer_is_atomic_on_failure(funded: GuitaService, monkeypatch) -> None:
    """If the second leg fails, no partial transfer remains."""
    original = funded._repo.add_transaction
    calls = {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("boom")
        return original(*args, **kwargs)

    monkeypatch.setattr(funded._repo, "add_transaction", flaky)
    with pytest.raises(RuntimeError):
        funded.transfer("100", "Wise", "Wallbit")

    assert funded.total_balance() == Decimal("1000.00")
    assert funded.account_balance(funded.get_account("Wise")) == Decimal("1000.00")
    assert funded.account_balance(funded.get_account("Wallbit")) == Decimal("0.00")
    assert all(tx.transfer_id is None for tx, _ in funded.history())
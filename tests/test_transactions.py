"""Additions, removals, and fees."""

from decimal import Decimal

import pytest

from guita.app.service import GuitaService
from guita.domain.errors import InsufficientBalanceError, ValidationError


def test_addition(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("100", "Wise")
    assert svc.account_balance(svc.get_account("Wise")) == Decimal("100.00")
    assert svc.total_balance() == Decimal("100.00")


def test_addition_multiple_amounts(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    tx, parts = svc.add_money(["42.5", "297.5"], "Upwork")
    assert parts == [Decimal("42.50"), Decimal("297.50")]
    assert tx.amount == Decimal("340.00")
    assert svc.account_balance(svc.get_account("Upwork")) == Decimal("340.00")
    assert svc.total_balance() == Decimal("340.00")


def test_removal_multiple_amounts(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("500", "Wise")
    tx, parts = svc.remove_money(["40", "10.5"], "Wise")
    assert parts == [Decimal("40.00"), Decimal("10.50")]
    assert tx.amount == Decimal("50.50")
    assert svc.account_balance(svc.get_account("Wise")) == Decimal("449.50")


def test_removal(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("100", "Wise")
    svc.remove_money("30", "Wise")
    assert svc.account_balance(svc.get_account("Wise")) == Decimal("70.00")


def test_addition_with_fee(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("100", "Wise", fee="5")
    assert svc.account_balance(svc.get_account("Wise")) == Decimal("95.00")
    assert svc.total_balance() == Decimal("95.00")


def test_removal_with_fee(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("200", "Wise")
    svc.remove_money("100", "Wise", fee="5")
    assert svc.account_balance(svc.get_account("Wise")) == Decimal("95.00")
    assert svc.total_balance() == Decimal("95.00")


def test_insufficient_balance_on_removal(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("50", "Wise")
    with pytest.raises(InsufficientBalanceError, match="50"):
        svc.remove_money("80", "Wise")


def test_invalid_amount(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    with pytest.raises(ValidationError):
        svc.add_money("0", "Wise")
    with pytest.raises(ValidationError):
        svc.add_money("-10", "Wise")
    with pytest.raises(ValidationError):
        svc.add_money("1.234", "Wise")


def test_persistence_across_reopen(db_path, svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_money("80", "Wise")
    svc.close()

    reopened = GuitaService(db_path)
    try:
        assert reopened.total_balance() == Decimal("80.00")
        assert reopened.account_balance(reopened.get_account("Wise")) == Decimal("80.00")
    finally:
        reopened.close()
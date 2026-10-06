"""Set account balance via corrective ledger entries."""

from decimal import Decimal

import pytest

from guita.app.service import GuitaService
from guita.domain.errors import ValidationError
from guita.domain.models import TransactionType


def test_set_balance_increases_with_addition(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    svc.add_money("200", "Upwork")
    account, previous, target, tx = svc.set_balance("Upwork", "1000")
    assert account.name == "Upwork"
    assert previous == Decimal("200.00")
    assert target == Decimal("1000.00")
    assert tx is not None
    assert tx.type is TransactionType.ADDITION
    assert tx.amount == Decimal("800.00")
    assert tx.description == "set"
    assert svc.account_balance(svc.get_account("Upwork")) == Decimal("1000.00")
    assert svc.total_balance() == Decimal("1000.00")


def test_set_balance_decreases_with_removal(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    svc.add_money("1500", "Upwork")
    _, previous, target, tx = svc.set_balance("upwork", "1000")
    assert previous == Decimal("1500.00")
    assert target == Decimal("1000.00")
    assert tx is not None
    assert tx.type is TransactionType.REMOVAL
    assert tx.amount == Decimal("500.00")
    assert svc.account_balance(svc.get_account("Upwork")) == Decimal("1000.00")


def test_set_balance_noop_when_already_target(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    svc.add_money("1000", "Upwork")
    before = len(svc.history())
    _, previous, target, tx = svc.set_balance("Upwork", "1000")
    assert previous == target == Decimal("1000.00")
    assert tx is None
    assert len(svc.history()) == before


def test_set_balance_allows_zero(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    svc.add_money("80", "Upwork")
    _, _, target, tx = svc.set_balance("Upwork", "0")
    assert target == Decimal("0.00")
    assert tx is not None
    assert svc.account_balance(svc.get_account("Upwork")) == Decimal("0.00")


def test_set_balance_rejects_negative(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    with pytest.raises(ValidationError, match="greater than or equal to zero"):
        svc.set_balance("Upwork", "-10")


def test_set_balance_accepts_comma_decimal(svc: GuitaService) -> None:
    svc.add_account("Upwork", "USD")
    svc.set_balance("Upwork", "1000,50")
    assert svc.account_balance(svc.get_account("Upwork")) == Decimal("1000.50")

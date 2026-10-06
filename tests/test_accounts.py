"""Account management."""

import pytest

from guita.app.service import GuitaService
from guita.domain.errors import ConflictError, NotFoundError, ValidationError


def test_add_and_list_accounts(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_account("Wallbit", "USD")
    names = [a.name for a in svc.list_accounts()]
    assert names == ["Wallbit", "Wise"]


def test_account_names_case_insensitive(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    with pytest.raises(ConflictError):
        svc.add_account("wise", "USD")
    found = svc.get_account("WISE")
    assert found.name == "Wise"


def test_reject_non_usd(svc: GuitaService) -> None:
    with pytest.raises(ValidationError, match="USD"):
        svc.add_account("Wise", "EUR")


def test_deactivate_blocks_transactions(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.deactivate_account("Wise")
    with pytest.raises(ConflictError, match="inactive"):
        svc.add_money("10", "Wise")


def test_unknown_account(svc: GuitaService) -> None:
    with pytest.raises(NotFoundError, match="wize"):
        svc.get_account("wize")
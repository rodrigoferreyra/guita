"""CLI argument order for add/remove amounts and account."""

from guita.cli.app import _split_amounts_and_account
from guita.domain.errors import ValidationError
import pytest


def test_account_last() -> None:
    amounts, account = _split_amounts_and_account(["100", "upwork"])
    assert amounts == ["100"]
    assert account == "upwork"


def test_account_first() -> None:
    amounts, account = _split_amounts_and_account(["upwork", "100"])
    assert amounts == ["100"]
    assert account == "upwork"


def test_multiple_amounts_either_side() -> None:
    amounts, account = _split_amounts_and_account(["42.5", "297.5", "upwork"])
    assert amounts == ["42.5", "297.5"]
    assert account == "upwork"

    amounts, account = _split_amounts_and_account(["upwork", "42,5", "297,5"])
    assert amounts == ["42,5", "297,5"]
    assert account == "upwork"


def test_known_account_wins_among_tokens( ) -> None:
    amounts, account = _split_amounts_and_account(
        ["100", "cash"],
        known_accounts=["Cash"],
    )
    assert amounts == ["100"]
    assert account == "cash"


def test_rejects_all_amounts() -> None:
    with pytest.raises(ValidationError, match="missing account name"):
        _split_amounts_and_account(["100", "200"])


def test_rejects_multiple_names() -> None:
    with pytest.raises(ValidationError, match="could not determine"):
        _split_amounts_and_account(["upwork", "wise", "100"])

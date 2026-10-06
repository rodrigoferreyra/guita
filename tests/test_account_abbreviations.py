"""Account short codes, aliases, and abbreviation resolution."""

from decimal import Decimal

import pytest

from guita.app.service import GuitaService
from guita.domain.errors import ConflictError, NotFoundError


def test_three_letter_abbreviation(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    account = svc.get_account("wis")
    assert account.name == "Wise"
    svc.add_money("10", "wis")
    assert svc.account_balance(account) == Decimal("10.00")


def test_reject_short_code_collision_and_offer_alias(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    with pytest.raises(ConflictError, match="--alias"):
        svc.add_account("Wisdom", "USD")


def test_create_with_alias_when_short_codes_overlap(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    wisdom = svc.add_account("Wisdom", "USD", alias="wdm")
    assert wisdom.alias == "wdm"
    assert svc.get_account("wis").name == "Wise"
    assert svc.get_account("wdm").name == "Wisdom"
    assert svc.get_account("Wisdom").name == "Wisdom"


def test_set_alias_on_existing_account(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    svc.add_account("Wallet", "USD", alias="wlt")
    updated = svc.set_alias("Wallet", "wll")
    assert updated.alias == "wll"
    assert svc.get_account("wll").name == "Wallet"


def test_alias_collision_rejected(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    with pytest.raises(ConflictError, match="overlaps"):
        svc.add_account("Other", "USD", alias="wis")


def test_abbreviation_too_short(svc: GuitaService) -> None:
    svc.add_account("Wise", "USD")
    with pytest.raises(NotFoundError, match="at least 3 letters"):
        svc.get_account("wi")


def test_cli_abbreviation_and_alias(tmp_path, monkeypatch) -> None:
    from typer.testing import CliRunner
    from guita.cli.app import app

    db = tmp_path / "abbr.db"
    monkeypatch.setenv("GUITA_DATABASE", str(db))
    runner = CliRunner()
    assert runner.invoke(app, ["account", "add", "Wise", "USD"]).exit_code == 0
    blocked = runner.invoke(app, ["account", "add", "Wisdom", "USD"])
    assert blocked.exit_code == 1
    assert "--alias" in blocked.stderr
    created = runner.invoke(
        app, ["account", "add", "Wisdom", "USD", "--alias", "wdm"]
    )
    assert created.exit_code == 0
    assert "wdm" in created.stdout
    assert runner.invoke(app, ["+", "10", "wis"]).exit_code == 0
    assert runner.invoke(app, ["+", "5", "wdm"]).exit_code == 0
    listed = runner.invoke(app, ["account", "list"])
    assert "short: wis" in listed.stdout
    assert "alias: wdm" in listed.stdout

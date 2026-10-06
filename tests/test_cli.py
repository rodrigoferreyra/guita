"""CLI smoke tests via Typer's CliRunner."""

from pathlib import Path

from typer.testing import CliRunner

from guita.cli.app import app

runner = CliRunner()


def test_short_and_long_help() -> None:
    long_help = runner.invoke(app, ["--help"])
    short_help = runner.invoke(app, ["-h"])
    assert long_help.exit_code == 0
    assert short_help.exit_code == 0
    assert "transfer" in short_help.stdout
    assert "-h" in short_help.stdout or "--help" in short_help.stdout

    transfer_help = runner.invoke(app, ["transfer", "-h"])
    assert transfer_help.exit_code == 0
    assert "destination" in transfer_help.stdout

    account_help = runner.invoke(app, ["account", "-h"])
    assert account_help.exit_code == 0
    assert "add" in account_help.stdout


def test_info_and_core_flow(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "cli.db"
    monkeypatch.setenv("GUITA_DATABASE", str(db))

    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Guita" in result.stdout
    assert str(db) in result.stdout

    assert runner.invoke(app, ["account", "add", "Wise", "USD"]).exit_code == 0
    assert runner.invoke(app, ["account", "add", "Wallbit", "USD"]).exit_code == 0
    assert runner.invoke(app, ["+", "1000", "wise"]).exit_code == 0
    multi = runner.invoke(app, ["+", "42.5", "297.5", "wise"])
    assert multi.exit_code == 0
    assert "340.00" in multi.stdout or "$340.00" in multi.stdout
    assert "42.50" in multi.stdout
    comma = runner.invoke(app, ["+", "10,5", "wise"])
    assert comma.exit_code == 0
    assert "10.50" in comma.stdout
    assert runner.invoke(app, ["-", "80", "Wise", "--fee", "2"]).exit_code == 0
    transfer = runner.invoke(app, ["transfer", "500", "wise", "wallbit", "--fee", "5"])
    assert transfer.exit_code == 0
    assert "Wallbit" in transfer.stdout
    assert "Fee" in transfer.stdout

    balance = runner.invoke(app, ["balance"])
    assert balance.exit_code == 0
    assert "Total" in balance.stdout

    # Default command shows balance
    default = runner.invoke(app, [])
    assert default.exit_code == 0
    assert "Total" in default.stdout

    history = runner.invoke(app, ["history"])
    assert history.exit_code == 0
    assert "Transfer" in history.stdout

    bad = runner.invoke(app, ["+", "10", "nope"])
    assert bad.exit_code == 1
    assert "does not exist" in bad.stderr

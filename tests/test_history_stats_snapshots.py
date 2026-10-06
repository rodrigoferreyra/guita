"""History, stats, snapshots, goals, export."""

from decimal import Decimal
from pathlib import Path

from guita.app.service import GuitaService


def test_history_and_filters(funded: GuitaService) -> None:
    funded.add_money("50", "Wallbit")
    funded.remove_money("20", "Wise")
    funded.transfer("100", "Wise", "Wallbit")

    all_rows = funded.history()
    assert len(all_rows) >= 4

    wise_only = funded.history(account_name="Wise")
    assert all(acct.name == "Wise" for _, acct in wise_only)

    transfers = funded.history(tx_type="transfer")
    assert all(
        tx.type.value.startswith("transfer") for tx, _ in transfers
    )


def test_stats_exclude_transfer_principal_from_net(funded: GuitaService) -> None:
    funded.transfer("400", "Wise", "Wallbit", fee="5")
    funded.remove_money("50", "Wise")
    stats = funded.stats()
    # Starting from funded fixture in "now" month: +1000 addition already present
    assert stats.transfer_volume == Decimal("400.00")
    assert stats.fees == Decimal("5.00")
    assert stats.removed == Decimal("50.00")
    # Net = added - removed - fees; transfers do not change net beyond fees
    assert stats.net_change == stats.added - stats.removed - stats.fees
    assert funded.total_balance() == Decimal("945.00")


def test_stats_all_time(funded: GuitaService) -> None:
    funded.transfer("400", "Wise", "Wallbit", fee="5")
    funded.remove_money("50", "Wise")
    all_time = funded.stats(all_time=True)
    assert all_time.starting_balance == Decimal("0.00")
    assert all_time.ending_balance == Decimal("945.00")
    assert all_time.added == Decimal("1000.00")
    assert all_time.removed == Decimal("50.00")
    assert all_time.fees == Decimal("5.00")
    assert all_time.net_change == Decimal("945.00")
    assert all_time.transfer_volume == Decimal("400.00")


def test_snapshot_does_not_alter_ledger(funded: GuitaService) -> None:
    before = funded.total_balance()
    snap, ledger = funded.snapshot("Wise", "900")
    assert funded.total_balance() == before
    assert ledger == Decimal("1000.00")
    assert snap.balance == Decimal("900.00")

    account, ledger_bal, actual, diff = funded.reconciliation("Wise")
    assert account.name == "Wise"
    assert ledger_bal == Decimal("1000.00")
    assert actual == Decimal("900.00")
    assert diff == Decimal("-100.00")


def test_goal_progress(funded: GuitaService) -> None:
    funded.set_goal("10000")
    current, goal, progress, remaining = funded.goal_progress()
    assert current == Decimal("1000.00")
    assert goal == Decimal("10000.00")
    assert progress == Decimal("10.0")
    assert remaining == Decimal("9000.00")


def test_export_csv_and_json(funded: GuitaService, tmp_path: Path) -> None:
    funded.transfer("100", "Wise", "Wallbit", fee="1")
    csv_path = tmp_path / "transactions.csv"
    json_path = tmp_path / "transactions.json"
    funded.export_transactions(csv_path)
    funded.export_transactions(json_path)
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "Wise" in csv_text
    assert "transfer_out" in csv_text or "transfer_in" in csv_text
    assert json_path.read_text(encoding="utf-8").strip().startswith("[")


def test_balance_history(funded: GuitaService) -> None:
    funded.remove_money("100", "Wise")
    points = funded.balance_history()
    assert points
    assert points[-1][1] == Decimal("900.00")
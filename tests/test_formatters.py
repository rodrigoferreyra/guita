"""CLI formatting helpers: colors and graphs."""

from decimal import Decimal

from guita.cli.formatters import color_text, display_money, format_stats
from guita.app.service import PeriodStats


def test_positive_green_negative_red() -> None:
    assert "\033[32m" in color_text("+$1.00", Decimal("1"), enabled=True)
    assert "\033[31m" in color_text("-$1.00", Decimal("-1"), enabled=True)
    assert "\033[32m" not in color_text("+$1.00", Decimal("1"), enabled=False)
    assert "\033[32m" in display_money(Decimal("5"), signed=True, color=True)
    assert "\033[31m" in display_money(Decimal("-5"), signed=True, color=True)


def test_stats_includes_graphs_and_all_time() -> None:
    month = PeriodStats(
        added=Decimal("100.00"),
        removed=Decimal("20.00"),
        fees=Decimal("2.00"),
        transfer_volume=Decimal("50.00"),
        net_change=Decimal("78.00"),
        starting_balance=Decimal("0.00"),
        ending_balance=Decimal("78.00"),
    )
    all_time = PeriodStats(
        added=Decimal("500.00"),
        removed=Decimal("100.00"),
        fees=Decimal("10.00"),
        transfer_volume=Decimal("200.00"),
        net_change=Decimal("390.00"),
        starting_balance=Decimal("0.00"),
        ending_balance=Decimal("390.00"),
    )
    text = format_stats(month, all_time, [])
    assert "This month" in text
    assert "All time" in text
    assert "Savings over time" in text
    assert "█" in text or "·" in text

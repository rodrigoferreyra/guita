"""CLI formatting helpers: colors and graphs."""

from datetime import datetime, timezone
from decimal import Decimal

from guita.app.service import PeriodStats
from guita.cli.charts import render_xy_chart
from guita.cli.formatters import color_text, display_money, format_stats


def test_positive_green_negative_red() -> None:
    assert "\033[32m" in color_text("+$1.00", Decimal("1"), enabled=True)
    assert "\033[31m" in color_text("-$1.00", Decimal("-1"), enabled=True)
    assert "\033[32m" not in color_text("+$1.00", Decimal("1"), enabled=False)
    assert "\033[32m" in display_money(Decimal("5"), signed=True, color=True)
    assert "\033[31m" in display_money(Decimal("-5"), signed=True, color=True)


def test_xy_chart_has_axes_and_points() -> None:
    chart = "\n".join(
        render_xy_chart(
            [
                ("Oct 01", Decimal("100")),
                ("Oct 02", Decimal("250")),
                ("Oct 03", Decimal("180")),
                ("Oct 04", Decimal("400")),
            ],
            title="Total savings",
        )
    )
    assert "Total savings" in chart
    assert "┤" in chart or "│" in chart
    assert "└" in chart
    assert "●" in chart
    assert "Oct 01" in chart
    assert "Oct 04" in chart


def test_stats_includes_two_axis_graphs_and_all_time() -> None:
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
    points = [
        (datetime(2026, 10, 1, tzinfo=timezone.utc), Decimal("100"), None),
        (datetime(2026, 10, 2, tzinfo=timezone.utc), Decimal("250"), Decimal("150")),
        (datetime(2026, 10, 3, tzinfo=timezone.utc), Decimal("200"), Decimal("-50")),
    ]
    text = format_stats(month, all_time, points)
    assert "This month" in text
    assert "All time" in text
    assert "Progression over time" in text
    assert "Total savings" in text
    assert "Daily change" in text
    assert "●" in text
    assert "└" in text

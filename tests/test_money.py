"""Money parsing and formatting."""

from decimal import Decimal

import pytest

from guita.domain.errors import ValidationError
from guita.domain.money import (
    format_money,
    parse_non_negative_fee,
    parse_positive_amount,
    sum_positive_amounts,
)


def test_parse_positive_amount() -> None:
    assert parse_positive_amount("80") == Decimal("80.00")
    assert parse_positive_amount("80.5") == Decimal("80.50")
    assert parse_positive_amount("80.50") == Decimal("80.50")


def test_comma_and_dot_decimal_separators() -> None:
    assert parse_positive_amount("42.5") == Decimal("42.50")
    assert parse_positive_amount("42,5") == Decimal("42.50")
    assert parse_positive_amount("1000,50") == Decimal("1000.50")
    assert parse_positive_amount("1.234,56") == Decimal("1234.56")
    assert parse_positive_amount("1,234.56") == Decimal("1234.56")
    assert parse_non_negative_fee("2,5") == Decimal("2.50")


def test_sum_with_commas() -> None:
    total, parts = sum_positive_amounts(["42,5", "297,5"])
    assert parts == [Decimal("42.50"), Decimal("297.50")]
    assert total == Decimal("340.00")


def test_reject_zero_and_negative() -> None:
    with pytest.raises(ValidationError):
        parse_positive_amount("0")
    with pytest.raises(ValidationError):
        parse_positive_amount("-1")


def test_reject_more_than_two_decimals() -> None:
    with pytest.raises(ValidationError, match="2 decimal"):
        parse_positive_amount("10.123")


def test_fee_non_negative() -> None:
    assert parse_non_negative_fee(None) == Decimal("0.00")
    assert parse_non_negative_fee("0") == Decimal("0.00")
    assert parse_non_negative_fee("2.5") == Decimal("2.50")
    with pytest.raises(ValidationError):
        parse_non_negative_fee("-1")


def test_sum_positive_amounts() -> None:
    total, parts = sum_positive_amounts(["42.5", "297.5"])
    assert parts == [Decimal("42.50"), Decimal("297.50")]
    assert total == Decimal("340.00")


def test_format_money() -> None:
    assert format_money(Decimal("1000")) == "$1,000.00"
    assert format_money(Decimal("80"), signed=True) == "+$80.00"
    assert format_money(Decimal("-80"), signed=True) == "-$80.00"
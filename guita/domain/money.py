"""Exact decimal money helpers. USD with two decimal places."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from guita.domain.errors import ValidationError

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def normalize_decimal_input(text: str) -> str:
    """Accept comma or dot as the decimal separator.

    Examples: ``42.5``, ``42,5``, ``1000,50``.
    If both ``.`` and ``,`` appear, the last separator is treated as decimal
    and the other as thousands grouping (``1.234,56`` / ``1,234.56``).
    """
    cleaned = text.strip().replace(" ", "").replace("\u00a0", "")
    if not cleaned:
        return cleaned

    # Allow a leading + or - for completeness; amounts validate positivity later.
    sign = ""
    if cleaned[0] in "+-":
        sign = cleaned[0]
        cleaned = cleaned[1:]

    has_dot = "." in cleaned
    has_comma = "," in cleaned

    if has_dot and has_comma:
        if cleaned.rfind(",") > cleaned.rfind("."):
            # 1.234,56
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # 1,234.56
            cleaned = cleaned.replace(",", "")
    elif has_comma:
        if cleaned.count(",") == 1:
            cleaned = cleaned.replace(",", ".")
        else:
            # 1,000,000 — thousands separators only
            cleaned = cleaned.replace(",", "")

    return sign + cleaned


def parse_money(value: str | Decimal, *, field: str = "amount") -> Decimal:
    """Parse a monetary value. Rejects non-numeric input and >2 decimal places."""
    if isinstance(value, Decimal):
        amount = value
    else:
        text = normalize_decimal_input(value)
        if not text:
            raise ValidationError(f"Error: {field} must be greater than zero.")
        try:
            amount = Decimal(text)
        except InvalidOperation as exc:
            raise ValidationError(
                f'Error: {field} "{value}" is not a valid number.'
            ) from exc

    if amount.is_nan() or amount.is_infinite():
        raise ValidationError(f'Error: {field} "{value}" is not a valid number.')

    if amount.as_tuple().exponent < -2:
        raise ValidationError(
            f"Error: {field} must have at most 2 decimal places "
            f'(got "{amount}").'
        )

    return amount.quantize(CENT)


def parse_positive_amount(value: str | Decimal, *, field: str = "amount") -> Decimal:
    amount = parse_money(value, field=field)
    if amount <= ZERO:
        raise ValidationError(f"Error: {field} must be greater than zero.")
    return amount


def sum_positive_amounts(
    values: list[str | Decimal] | str | Decimal,
    *,
    field: str = "amount",
) -> tuple[Decimal, list[Decimal]]:
    """Parse one or more positive amounts and return (total, parts)."""
    if isinstance(values, (str, Decimal)):
        parts_in: list[str | Decimal] = [values]
    else:
        parts_in = list(values)

    if not parts_in:
        raise ValidationError(f"Error: {field} must be greater than zero.")

    parts = [
        parse_positive_amount(value, field=f"{field} '{value}'" if len(parts_in) > 1 else field)
        for value in parts_in
    ]
    total = sum(parts, ZERO).quantize(CENT)
    return total, parts


def parse_non_negative_fee(value: str | Decimal | None) -> Decimal:
    if value is None:
        return ZERO
    fee = parse_money(value, field="fee")
    if fee < ZERO:
        raise ValidationError("Error: fee must be greater than or equal to zero.")
    return fee


def format_money(amount: Decimal, *, signed: bool = False) -> str:
    """Format USD for display."""
    quantized = amount.quantize(CENT)
    absolute = f"${quantized.copy_abs():,.2f}"
    if signed:
        if quantized > ZERO:
            return f"+{absolute}"
        if quantized < ZERO:
            return f"-{absolute}"
        return absolute
    if quantized < ZERO:
        return f"-{absolute}"
    return absolute
"""Terminal X/Y charts for progression over time."""

from __future__ import annotations

from decimal import Decimal

from guita.domain.money import ZERO


def _compact_money(amount: Decimal) -> str:
    """Short Y-axis label."""
    quantized = amount.quantize(Decimal("0.01"))
    absolute = abs(quantized)
    if absolute >= Decimal("1000"):
        scaled = absolute / Decimal("1000")
        label = f"${scaled:.1f}k".replace(".0k", "k")
    elif absolute == absolute.to_integral_value():
        label = f"${absolute:,.0f}"
    else:
        label = f"${absolute:,.2f}"
    if quantized < ZERO:
        return f"-{label}"
    return label


def render_xy_chart(
    points: list[tuple[str, Decimal]],
    *,
    title: str,
    height: int = 8,
    width: int = 40,
) -> list[str]:
    """Render a two-axis chart: X = time labels, Y = values."""
    if not points:
        return [title, "  (no data yet)"]

    sample = points if len(points) <= width else _downsample(points, width)
    values = [value for _, value in sample]
    y_min = min(values)
    y_max = max(values)
    if y_min == y_max:
        pad = Decimal("1.00") if y_min == ZERO else abs(y_min) * Decimal("0.1")
        if pad == ZERO:
            pad = Decimal("1.00")
        y_min -= pad
        y_max += pad

    span = y_max - y_min
    cols = len(sample)
    rows = max(3, height)

    ys: list[int] = []
    for _, value in sample:
        ratio = float((value - y_min) / span)
        y = rows - 1 - int(round(ratio * (rows - 1)))
        ys.append(min(rows - 1, max(0, y)))

    marks: dict[tuple[int, int], str] = {}
    for x in range(cols - 1):
        y_a, y_b = ys[x], ys[x + 1]
        if abs(y_b - y_a) <= 1:
            continue
        step = 1 if y_b > y_a else -1
        for y in range(y_a + step, y_b, step):
            marks[(x, y)] = "·"
    for x, y in enumerate(ys):
        marks[(x, y)] = "●"

    label_width = max(
        len(_compact_money(y_min)),
        len(_compact_money(y_max)),
        len(_compact_money(y_min + span / 2)),
        6,
    )
    tick_rows = {
        0: y_max,
        rows // 2: y_min + span * Decimal(rows - 1 - rows // 2) / Decimal(rows - 1),
        rows - 1: y_min,
    }

    lines = [title]
    for row in range(rows):
        if row in tick_rows:
            label = _compact_money(tick_rows[row]).rjust(label_width)
            axis = "┤"
        else:
            label = " " * label_width
            axis = "│"
        cells = "".join(marks.get((col, row), " ") for col in range(cols))
        lines.append(f"  {label} {axis}{cells}")

    lines.append(f"  {' ' * label_width} └{'─' * cols}")
    x_labels = _x_axis_labels([label for label, _ in sample], cols)
    lines.append(f"  {' ' * (label_width + 2)}{x_labels}")
    return lines


def _downsample(
    points: list[tuple[str, Decimal]],
    width: int,
) -> list[tuple[str, Decimal]]:
    if width < 2 or len(points) <= width:
        return points
    result = [points[0]]
    inner = width - 2
    for i in range(inner):
        idx = 1 + int((i + 1) * (len(points) - 2) / (inner + 1))
        result.append(points[idx])
    result.append(points[-1])
    return result


def _x_axis_labels(labels: list[str], cols: int) -> str:
    if not labels:
        return ""
    if len(labels) == 1 or cols == 1:
        return labels[0]

    first = labels[0]
    last = labels[-1]
    # Keep first and last fully visible; pad the middle to at least the plot width.
    gap = max(2, cols - len(first) - len(last))
    line = first + (" " * gap) + last

    if cols >= 10 and len(labels) >= 3:
        mid = labels[len(labels) // 2]
        center = len(first) + gap // 2
        start = max(len(first) + 1, center - len(mid) // 2)
        end = start + len(mid)
        if end < len(line) - len(last) - 1:
            chars = list(line)
            for i, ch in enumerate(mid):
                chars[start + i] = ch
            line = "".join(chars)
    return line

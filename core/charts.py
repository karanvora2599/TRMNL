SPARK_BLOCKS = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    n = len(SPARK_BLOCKS)
    return "".join(SPARK_BLOCKS[min(int((v - lo) / span * (n - 1)), n - 1)] for v in values)


def _fmt_k(val: float) -> str:
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:.1f}M"
    if abs(val) >= 1_000:
        return f"${val / 1_000:.0f}k"
    return f"${val:.0f}"


def horizontal_bars(
    items: list[tuple[str, float]],
    label_width: int = 14,
    bar_width: int = 20,
    color: str = "flag",
) -> list[str]:
    if not items:
        return []
    max_val = max(v for _, v in items) or 1
    lines = []
    for label, val in items:
        frac = val / max_val
        filled = round(frac * bar_width)
        bar_str = "█" * filled + "░" * (bar_width - filled)
        label_str = label[:label_width].ljust(label_width)
        lines.append(
            f"  [muted]{label_str}[/muted]  [{color}]{bar_str}[/{color}]  [val]${val:,.2f}[/val]"
        )
    return lines


def line_chart(
    labels: list[str],
    values: list[float],
    height: int = 7,
    col_width: int = 8,
    color: str = "flag",
) -> list[str]:
    if not values or len(values) < 2:
        return ["  [muted]not enough data[/muted]"]
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    n = len(values)

    def row_for(v: float) -> int:
        return height - 1 - round((v - lo) / span * (height - 1))

    grid = [[" " * col_width for _ in range(n)] for _ in range(height)]
    for ci, val in enumerate(values):
        r = row_for(val)
        grid[r][ci] = ("*" + " " * (col_width - 1))

    lines = []
    for ri, row in enumerate(grid):
        if ri == 0:
            y_label = _fmt_k(hi)
        elif ri == height - 1:
            y_label = _fmt_k(lo)
        else:
            y_label = ""
        y_label = y_label[:6].rjust(6)
        row_str = "".join(row)
        lines.append(f"  [muted]{y_label}[/muted]  [{color}]{row_str}[/{color}]")

    if labels:
        step = max(1, n // 6)
        label_parts = []
        for ci, lbl in enumerate(labels):
            if ci % step == 0 or ci == n - 1:
                label_parts.append(lbl[:col_width].ljust(col_width))
            else:
                label_parts.append(" " * col_width)
        lines.append(f"  [muted]        [/muted]  [dim]{''.join(label_parts)}[/dim]")

    return lines

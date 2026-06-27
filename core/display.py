import sys

from rich.console import Console
from rich.theme import Theme

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

THEME = Theme(
    {
        "cmd":    "#d45858",
        "val":    "#5cb87a",
        "flag":   "#7ea8d4",
        "user":   "#c4985a",
        "muted":  "#6b6b6b",
        "dim":    "#333333",
        "brand":  "#545454",
        "purple": "#9b7fd4",
        "teal":   "#5cb8b2",
    }
)

console = Console(theme=THEME, highlight=False, force_terminal=True, legacy_windows=False)

CATEGORY_STYLE = {
    "grocery":        "flag",
    "food":           "user",
    "subscriptions":  "purple",
    "shopping":       "val",
    "transfer":       "muted",
    "income":         "val",
    "utilities":      "cmd",
    "transportation": "flag",
    "health":         "teal",
    "travel":         "teal",
    "hotel":          "teal",
    "dining":         "user",
    "entertainment":  "purple",
    "fees":           "cmd",
}


def cat_style(category: str) -> str:
    return CATEGORY_STYLE.get(category, "muted")


def fmt_amount(amount: float, txn_type: str) -> str:
    if txn_type == "credit":
        return f"[val]+${amount:,.2f}[/val]"
    return f"[cmd]-${amount:,.2f}[/cmd]"


def fmt_date(iso: str) -> str:
    from datetime import datetime
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%m/%d")


def bar(fraction: float, width: int = 20) -> str:
    fraction = min(max(fraction, 0.0), 1.0)
    filled = round(fraction * width)
    return "█" * filled + "░" * (width - filled)


def error(msg: str):
    console.print(f"  [cmd]error:[/cmd] [muted]{msg}[/muted]")


def success(msg: str):
    console.print(f"  [val]{msg}[/val]")


def info(msg: str):
    console.print(f"  [muted]{msg}[/muted]")

from rich.console import Console
from rich.theme import Theme

THEME = Theme(
    {
        "cmd":   "#d45858",
        "val":   "#5cb87a",
        "flag":  "#7ea8d4",
        "user":  "#c4985a",
        "muted": "#545454",
        "dim":   "#2e2e2e",
        "brand": "#6b6b6b",
    }
)

console = Console(theme=THEME, highlight=False)


def prompt_str(username: str) -> str:
    return f"[brand]{username}$[/brand] "


def print_prompt(username: str):
    console.print(prompt_str(username), end="")


def fmt_amount(amount: float, txn_type: str) -> str:
    if txn_type == "credit":
        return f"[val]+${amount:,.2f}[/val]"
    return f"[cmd]-${amount:,.2f}[/cmd]"


def fmt_date(iso: str) -> str:
    from datetime import datetime
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%m/%d")


def error(msg: str):
    console.print(f"[cmd]error:[/cmd] [muted]{msg}[/muted]")


def success(msg: str):
    console.print(f"[val]{msg}[/val]")


def info(msg: str):
    console.print(f"[muted]{msg}[/muted]")

from collections import defaultdict
from datetime import datetime

from core.display import console, bar, cat_style, info, error
from core.parser import ParsedCommand
from core.store import Store

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def cmd_spend(store: Store, cmd: ParsedCommand):
    top_n = int(cmd.flags.get("top", 5))
    month_raw = cmd.flags.get("month")
    now = datetime.now()

    month, year = now.month, now.year
    if month_raw:
        m = str(month_raw).lower()
        if m in MONTH_NAMES:
            month = MONTH_NAMES[m]
        else:
            try:
                month = int(month_raw)
            except ValueError:
                error(f"unrecognised month '{month_raw}'")
                return

    acct = store.get_default_account()
    txns = store.get_transactions(account_id=acct["id"], month=month, year=year)
    debits = [t for t in txns if t["type"] != "credit"]

    if not debits:
        info(f"no spending data for {datetime(year, month, 1).strftime('%B %Y')}")
        return

    by_merchant: dict[str, float] = defaultdict(float)
    by_merchant_cat: dict[str, str] = {}
    by_category: dict[str, float] = defaultdict(float)

    for t in debits:
        name = t["merchant"]["name"]
        cat = t["merchant"]["category"]
        by_merchant[name] += t["amount"]
        by_merchant_cat[name] = cat
        by_category[cat] += t["amount"]

    total = sum(by_category.values())
    month_name = datetime(year, month, 1).strftime("%B %Y")
    max_bar = max(by_category.values())

    console.print(f"\n  [brand]spend[/brand]  [muted]{month_name}[/muted]  [dim]total [/dim][cmd]-${total:,.2f}[/cmd]\n")

    console.print(f"  [dim]top {top_n} merchants[/dim]")
    top = sorted(by_merchant.items(), key=lambda x: x[1], reverse=True)[:top_n]
    for i, (name, amt) in enumerate(top, 1):
        cat = by_merchant_cat[name]
        style = cat_style(cat)
        pct = amt / total * 100
        console.print(
            f"  [dim]{i}.[/dim]  {name:<30}  [cmd]-${amt:>8,.2f}[/cmd]"
            f"  [{style}]{cat}[/{style}]  [dim]{pct:.1f}%[/dim]"
        )

    console.print(f"\n  [dim]by category[/dim]")
    for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        style = cat_style(cat)
        b = bar(amt / max_bar, width=14)
        pct = amt / total * 100
        console.print(
            f"  [{style}]{cat:<16}[/{style}]  [{style}]{b}[/{style}]"
            f"  [cmd]-${amt:>8,.2f}[/cmd]  [dim]{pct:5.1f}%[/dim]"
        )

    console.print()

from collections import defaultdict
from datetime import datetime

from core.display import console, bar, cat_style, info, error
from core.parser import ParsedCommand
from core.store import Store

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def cmd_budget(store: Store, cmd: ParsedCommand):
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
    budgets = {b["category"]: b["limit"] for b in store.get_budgets()}

    spending: dict[str, float] = defaultdict(float)
    for t in txns:
        if t["type"] != "credit":
            spending[t["merchant"]["category"]] += t["amount"]

    if not spending:
        info(f"no spending data for {datetime(year, month, 1).strftime('%B %Y')}")
        return

    month_name = datetime(year, month, 1).strftime("%B %Y")
    console.print(f"\n  [brand]budget[/brand]  [muted]{month_name}[/muted]\n")

    tracked = {k: v for k, v in spending.items() if k in budgets}
    untracked = {k: v for k, v in spending.items() if k not in budgets}

    for cat in sorted(tracked, key=lambda c: spending[c], reverse=True):
        spent = tracked[cat]
        limit = budgets[cat]
        frac = spent / limit
        b = bar(frac)
        style = cat_style(cat)
        pct = frac * 100
        over_tag = "  [cmd]OVER[/cmd]" if frac > 1.0 else ""
        console.print(
            f"  [muted]{cat:<16}[/muted]  [{style}]{b}[/{style}]"
            f"  [{style}]${spent:>7,.2f}[/{style}] [dim]/ ${limit:,.2f}  {pct:5.1f}%[/dim]{over_tag}"
        )

    if untracked:
        console.print(f"\n  [dim]no limit:[/dim]")
        for cat in sorted(untracked, key=lambda c: untracked[c], reverse=True):
            style = cat_style(cat)
            console.print(
                f"  [muted]{cat:<16}[/muted]  [dim]{'·' * 20}[/dim]"
                f"  [{style}]${untracked[cat]:>7,.2f}[/{style}]"
            )

    console.print()

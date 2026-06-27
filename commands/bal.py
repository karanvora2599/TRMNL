from datetime import datetime

from core.display import console, error
from core.parser import ParsedCommand
from core.store import Store


def cmd_bal(store: Store, cmd: ParsedCommand):
    acct_filter = cmd.flags.get("acct")
    accounts = store.get_accounts_by_category("depository")

    if acct_filter:
        accounts = [a for a in accounts if a["type"].lower() == acct_filter.lower()]
        if not accounts:
            error(f"no account '{acct_filter}' -- try checking or savings")
            return

    console.print()
    for a in accounts:
        apy = f"  [dim]APY {a['apy']*100:.2f}%[/dim]" if "apy" in a else ""
        status_tag = f"  [cmd]({a['status']})[/cmd]" if a["status"] != "active" else ""
        avail = (
            f"  [dim]avail ${a['available_balance']:,.2f}[/dim]"
            if a["available_balance"] != a["balance"] else ""
        )
        console.print(
            f"  [muted]{a['type']:<12} ....{a['account_number_last4']}[/muted]"
            f"  [val]${a['balance']:>11,.2f}[/val]{avail}{apy}{status_tag}"
        )

    if not acct_filter:
        now = datetime.now()
        default = store.get_default_account()
        txns = store.get_transactions(account_id=default["id"], month=now.month, year=now.year)
        spent = sum(t["amount"] for t in txns if t["type"] != "credit")
        income = sum(t["amount"] for t in txns if t["type"] == "credit")
        month_label = now.strftime("%b").lower()
        console.print(
            f"\n  [dim]{month_label} out[/dim]  [cmd]-${spent:>9,.2f}[/cmd]"
            f"    [dim]in[/dim]  [val]+${income:>9,.2f}[/val]"
        )

    console.print()

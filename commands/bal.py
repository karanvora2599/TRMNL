from core.display import console
from core.parser import ParsedCommand
from core.store import Store


def cmd_bal(store: Store, cmd: ParsedCommand):
    acct_filter = cmd.flags.get("acct")

    accounts = store.get_accounts()
    if acct_filter:
        accounts = [a for a in accounts if a["type"].lower() == acct_filter.lower()]
        if not accounts:
            from core.display import error
            error(f"no account '{acct_filter}' -- try checking or savings")
            return

    for a in accounts:
        status_tag = "" if a["status"] == "active" else f" [dim]({a['status']})[/dim]"
        apy = f"  [dim]APY {a['apy']*100:.2f}%[/dim]" if "apy" in a else ""
        console.print(
            f"  [muted]{a['type']:<12}[/muted]  [val]${a['balance']:>10,.2f}[/val]"
            f"{apy}{status_tag}"
        )

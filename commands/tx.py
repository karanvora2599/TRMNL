from core.display import console, fmt_amount, fmt_date, cat_style, error
from core.parser import ParsedCommand
from core.store import Store


def cmd_tx(store: Store, cmd: ParsedCommand):
    acct_query = cmd.flags.get("acct")
    limit = int(cmd.flags["last"]) if "last" in cmd.flags else None

    if acct_query:
        acct = store.find_account(str(acct_query))
        if not acct:
            error(f"no account matching '{acct_query}'")
            return
        acct_id = acct["id"]
    else:
        acct_id = store.get_default_account()["id"]

    txns = store.get_transactions(account_id=acct_id, limit=limit)

    if cmd.pipe_grep:
        term = cmd.pipe_grep.lower()
        txns = [
            t for t in txns
            if term in t["merchant"]["name"].lower()
            or term in (t.get("memo") or "").lower()
            or term in t["merchant"]["category"].lower()
        ]

    if not txns:
        console.print("  [muted]no transactions found[/muted]")
        return

    console.print()
    for t in txns:
        date = fmt_date(t["created_at"])
        name = t["merchant"]["name"]
        cat = t["merchant"]["category"]
        style = cat_style(cat)
        memo = f"  [dim]{t['memo']}[/dim]" if t.get("memo") else ""
        pending = "  [dim]pending[/dim]" if t["status"] == "pending" else ""
        amount = fmt_amount(t["amount"], t["type"])
        console.print(
            f"  [muted]{date}[/muted]"
            f"  {name:<28}"
            f"  [{style}]{cat:<16}[/{style}]"
            f"  {amount}{memo}{pending}"
        )
    console.print()

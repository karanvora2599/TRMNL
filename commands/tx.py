from core.display import console, fmt_amount, fmt_date
from core.parser import ParsedCommand
from core.store import Store


def cmd_tx(store: Store, cmd: ParsedCommand):
    acct_type = cmd.flags.get("acct")
    limit = int(cmd.flags["last"]) if "last" in cmd.flags else None

    if acct_type:
        acct = store.get_account(acct_type=acct_type)
        if not acct:
            from core.display import error
            error(f"no account '{acct_type}'")
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

    for t in txns:
        date = fmt_date(t["created_at"])
        name = t["merchant"]["name"]
        memo = f"  [dim]{t['memo']}[/dim]" if t.get("memo") else ""
        pending = "  [dim]pending[/dim]" if t["status"] == "pending" else ""
        amount = fmt_amount(t["amount"], t["type"])
        console.print(f"  [muted]{date}[/muted]  {name:<28}{amount}{memo}{pending}")

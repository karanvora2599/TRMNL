import uuid
from datetime import datetime, timezone

from core.display import console, error, info
from core.parser import ParsedCommand
from core.store import Store


def cmd_transfer(store: Store, cmd: ParsedCommand):
    args = cmd.args

    try:
        to_idx = [a.lower() for a in args].index("to")
    except ValueError:
        error("usage: transfer <amt> to <savings|checking>")
        return

    if to_idx == 0 or to_idx + 1 >= len(args):
        error("usage: transfer <amt> to <savings|checking>")
        return

    try:
        amount = float(args[0])
    except ValueError:
        error(f"invalid amount '{args[0]}'")
        return

    if amount <= 0:
        error("amount must be positive")
        return

    dest_type = args[to_idx + 1].lower()
    if dest_type not in ("savings", "checking"):
        error("destination must be 'savings' or 'checking'")
        return

    src = store.get_default_account()
    dest = store.get_account(acct_type=dest_type)

    if dest is None:
        error(f"no {dest_type} account found")
        return

    if src["id"] == dest["id"]:
        error("source and destination are the same account")
        return

    if amount > src["available_balance"]:
        error(f"insufficient funds  --  available ${src['available_balance']:,.2f}")
        return

    console.print(
        f"\n  [muted]confirm [/muted][val]${amount:,.2f}[/val]"
        f"[muted]  {src['type']} -> {dest_type}[/muted]  [dim][y/n][/dim] ",
        end="",
    )

    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print()
        info("cancelled")
        return

    if answer != "y":
        info("cancelled")
        return

    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    store.add_transaction({
        "id": f"txn_{uuid.uuid4().hex[:20].upper()}",
        "account_id": src["id"],
        "type": "transfer",
        "amount": round(amount, 2),
        "currency": "USD",
        "merchant": {"name": f"Transfer to {dest_type}", "category": "transfer", "category_code": "6012"},
        "memo": f"-> {dest_type}",
        "destination_account_id": dest["id"],
        "status": "settled",
        "created_at": now_str,
        "settled_at": now_str,
    })
    store.add_transaction({
        "id": f"txn_{uuid.uuid4().hex[:20].upper()}",
        "account_id": dest["id"],
        "type": "credit",
        "amount": round(amount, 2),
        "currency": "USD",
        "merchant": {"name": f"Transfer from {src['type']}", "category": "transfer", "category_code": "6012"},
        "memo": f"<- {src['type']}",
        "source_account_id": src["id"],
        "status": "settled",
        "created_at": now_str,
        "settled_at": now_str,
    })

    store.update_balance(src["id"], -amount)
    store.update_balance(dest["id"], amount)

    src_new = store.get_account(acct_id=src["id"])
    dest_new = store.get_account(acct_type=dest_type)
    assert src_new and dest_new
    console.print(
        f"  [val]done[/val]  [muted]${amount:,.2f} moved"
        f"  /  {src['type']} ${src_new['balance']:,.2f}"
        f"  /  {dest_type} ${dest_new['balance']:,.2f}[/muted]\n"
    )

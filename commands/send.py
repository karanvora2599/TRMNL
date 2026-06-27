import uuid
from datetime import datetime, timezone

from core.display import console, error, info
from core.parser import ParsedCommand
from core.store import Store


def cmd_send(store: Store, cmd: ParsedCommand):
    # send <amt> to <user> [--memo <text>] [--recurring]
    args = cmd.args

    # parse positional: <amt> to <user>
    try:
        to_idx = [a.lower() for a in args].index("to")
    except ValueError:
        error("usage: send <amt> to <user> [--memo <text>] [--recurring]")
        return

    if to_idx == 0 or to_idx + 1 >= len(args):
        error("usage: send <amt> to <user> [--memo <text>] [--recurring]")
        return

    try:
        amount = float(args[0])
    except ValueError:
        error(f"invalid amount '{args[0]}'")
        return

    if amount <= 0:
        error("amount must be positive")
        return

    recipient = args[to_idx + 1].lstrip("@")
    memo = cmd.flags.get("memo")
    recurring = cmd.flags.get("recurring", False)

    contact = store.get_contact(recipient)
    if not contact:
        error(f"@{recipient} not found — add them as a contact first")
        return

    acct = store.get_default_account()
    if acct["available_balance"] < amount:
        error(f"insufficient funds — available ${acct['available_balance']:,.2f}")
        return

    memo_str = f" · {memo}" if memo else ""
    console.print(
        f"  [muted]confirm [/muted][val]${amount:,.2f}[/val][muted] · "
        f"[/muted][user]@{recipient}[/user][muted]{memo_str}[/muted]"
        f"  [dim][y/n][/dim]",
        end="  ",
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

    txn = {
        "id": f"txn_{uuid.uuid4().hex[:20].upper()}",
        "account_id": acct["id"],
        "type": "transfer",
        "amount": round(amount, 2),
        "currency": "USD",
        "merchant": {"name": f"@{recipient}", "category": "transfer", "category_code": "6012"},
        "memo": memo,
        "status": "settled",
        "contact_username": recipient,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "settled_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    store.add_transaction(txn)
    store.update_balance(acct["id"], -amount)

    if recurring:
        from datetime import date
        rec = {
            "id": f"recur_{uuid.uuid4().hex[:20].upper()}",
            "account_id": acct["id"],
            "payee_username": recipient,
            "payee_display_name": contact["display_name"],
            "amount": round(amount, 2),
            "currency": "USD",
            "memo": memo,
            "frequency": "monthly",
            "day_of_month": date.today().day,
            "next_date": str(date.today().replace(month=date.today().month % 12 + 1)),
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        store.add_recurring(rec)
        console.print(f"  [val]sent[/val]  [muted]${amount:,.2f} → @{recipient} · recurring monthly[/muted]")
    else:
        console.print(f"  [val]sent[/val]  [muted]${amount:,.2f} → @{recipient}[/muted]")

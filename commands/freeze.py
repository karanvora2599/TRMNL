from core.display import console, error, info
from core.parser import ParsedCommand
from core.store import Store


def cmd_freeze(store: Store, cmd: ParsedCommand):
    freezing = cmd.name == "freeze"
    target_status = "frozen" if freezing else "active"

    cards = store.get_cards()
    if not cards:
        error("no cards on this account")
        return

    card = cards[0]

    if card["status"] == target_status:
        info(f"card ****{card['last4']} is already {target_status}")
        return

    store.set_card_status(card["id"], target_status)

    if freezing:
        console.print(f"  [cmd]frozen[/cmd]  [muted]****{card['last4']} / {card['network'].upper()} / no new charges will be authorized[/muted]")
    else:
        console.print(f"  [val]active[/val]   [muted]****{card['last4']} / {card['network'].upper()} / card reactivated[/muted]")

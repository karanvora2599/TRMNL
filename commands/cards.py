from datetime import datetime

from core.display import console, info
from core.parser import ParsedCommand
from core.store import Store


def cmd_cards(store: Store, cmd: ParsedCommand):
    cards = store.get_cards()

    if not cards:
        info("no cards on this account")
        return

    console.print()
    for c in cards:
        status_style = "val" if c["status"] == "active" else "cmd"
        expires = datetime.strptime(c["expires_at"], "%Y-%m").strftime("%b %Y")
        console.print(
            f"  [muted]{c['nickname']:<18}[/muted]"
            f"  [muted]{c['network'].upper():<6}[/muted]"
            f"  ****{c['last4']}"
            f"  [{status_style}]{c['status']:<8}[/{status_style}]"
            f"  [dim]exp {expires}[/dim]"
        )
    console.print()

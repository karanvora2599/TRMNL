from core.display import console, info
from core.parser import ParsedCommand
from core.store import Store


def cmd_contacts(store: Store, cmd: ParsedCommand):
    query = cmd.args[0].lower().lstrip("@") if cmd.args else None
    contacts = store.get_contacts()

    if query:
        contacts = [
            c for c in contacts
            if query in c["username"].lower() or query in c["display_name"].lower()
        ]

    if not contacts:
        info("no contacts found")
        return

    console.print()
    for c in contacts:
        verified = "[val]verified[/val]" if c["verified"] else "[cmd]unverified[/cmd]"
        console.print(
            f"  [user]@{c['username']:<14}[/user]"
            f"  [muted]{c['display_name']:<22}[/muted]"
            f"  {verified}"
        )
    console.print()

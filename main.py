import os
import sys
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML

from core.store import Store
from core.parser import parse_line
from core.display import console, error
from commands import COMMANDS

_HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".trmnl_history")


def _greeting() -> str:
    h = datetime.now().hour
    if h < 12:
        return "good morning"
    if h < 17:
        return "good afternoon"
    return "good evening"


def _print_banner(store: Store):
    user = store.get_user()
    accounts = [a for a in store.get_accounts() if a.get("account_category") == "depository"]
    nw = store.compute_net_worth()

    acct_parts = "  ".join(
        f"[muted]{a['type']}[/muted]  [val]${a['balance']:,.2f}[/val]"
        for a in accounts
    )

    console.print()
    console.print(f"  [brand]TRMNL[/brand]  [dim]v0.1  /  terminal banking[/dim]")
    console.print()
    console.print(f"  [muted]{_greeting()}, {user['display_name'].split()[0].lower()}.[/muted]")
    console.print(f"  {acct_parts}  [dim]|[/dim]  [dim]net worth[/dim]  [val]${nw['net_worth']:,.2f}[/val]")
    console.print()
    console.print(f"  [dim]type [/dim][flag]help[/flag][dim] to see all commands[/dim]")
    console.print()


def main():
    store = Store()
    user = store.get_user()
    username = user["username"]

    _print_banner(store)

    session = PromptSession(
        history=FileHistory(_HISTORY_FILE),
        mouse_support=False,
    )

    prompt_html = HTML(f'<ansibrightblack>{username}$</ansibrightblack> ')

    while True:
        try:
            raw = session.prompt(prompt_html)
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print(f"\n  [muted]logged out.[/muted]\n")
            break

        raw = raw.strip()
        if not raw:
            continue

        if raw.lower() in ("exit", "quit", "logout"):
            console.print(f"\n  [muted]logged out.[/muted]\n")
            break

        if raw.lower() == "whoami":
            console.print(
                f"\n  [user]{user['display_name']}[/user]"
                f"  [muted]@{username}  /  {user['email']}  /  {user['kyc_status']}[/muted]\n"
            )
            continue

        if raw.lower() == "clear":
            os.system("cls" if sys.platform == "win32" else "clear")
            _print_banner(store)
            continue

        cmd = parse_line(raw)
        if cmd is None:
            continue

        handler = COMMANDS.get(cmd.name)
        if handler is None:
            error(f"unknown command '{cmd.name}'  --  type [flag]help[/flag]")
            continue

        try:
            handler(store, cmd)
        except Exception as exc:
            error(f"unexpected error: {exc}")


if __name__ == "__main__":
    main()

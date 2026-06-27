import os
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from core.store import Store
from core.parser import parse_line
from core.display import console, error
from commands import COMMANDS

_HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".trmnl_history")
_BANNER = """
[brand]TRMNL[/brand]  [dim]v0.1  terminal banking[/dim]
[dim]type [/dim][cmd]help[/cmd][dim] to see available commands[/dim]
"""


def main():
    store = Store()
    user = store.get_user()
    username = user["username"]

    console.print(_BANNER)

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
            console.print(f"\n[muted]logout[/muted]")
            break

        raw = raw.strip()
        if not raw:
            continue

        if raw.lower() in ("exit", "quit", "logout"):
            console.print(f"[muted]logout[/muted]")
            break

        if raw.lower() == "whoami":
            console.print(
                f"  [user]{user['display_name']}[/user]  [muted]@{username} · {user['email']} · {user['kyc_status']}[/muted]"
            )
            continue

        if raw.lower() == "clear":
            os.system("cls" if sys.platform == "win32" else "clear")
            continue

        cmd = parse_line(raw)
        if cmd is None:
            continue

        handler = COMMANDS.get(cmd.name)
        if handler is None:
            error(f"unknown command '{cmd.name}' — type [cmd]help[/cmd]")
            continue

        try:
            handler(store, cmd)
        except Exception as exc:
            error(f"unexpected error: {exc}")


if __name__ == "__main__":
    main()

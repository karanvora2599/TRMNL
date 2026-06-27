from core.display import console
from core.parser import ParsedCommand
from core.store import Store

HELP = {
    "bal": {
        "usage": "bal [--acct <checking|savings>]",
        "desc":  "Show account balances. Defaults to all accounts.",
        "examples": ["bal", "bal --acct savings"],
    },
    "send": {
        "usage": "send <amt> to <user> [--memo <text>] [--recurring]",
        "desc":  "Send money to a contact. Prompts for confirmation.",
        "examples": ["send 58 to @maya --memo 'rent'", "send 100 to @jay --recurring"],
    },
    "tx": {
        "usage": "tx [--last <n>] [--acct <type>] [| grep <term>]",
        "desc":  "List transactions. Supports grep-style filtering.",
        "examples": ["tx --last 10", "tx --last 20 | grep amazon", "tx --acct savings"],
    },
    "statement": {
        "usage": "statement [--month <mon>] [--year <year>] [--format <text|csv>]",
        "desc":  "Show a monthly statement. Optionally save to file.",
        "examples": ["statement --month may", "statement --month jun --format csv"],
    },
    "freeze": {
        "usage": "freeze card",
        "desc":  "Immediately freeze your debit card. No new charges authorized.",
        "examples": ["freeze card"],
    },
    "unfreeze": {
        "usage": "unfreeze card",
        "desc":  "Reactivate a frozen card.",
        "examples": ["unfreeze card"],
    },
    "help": {
        "usage": "help [<cmd>]",
        "desc":  "Show this help, or detailed help for a specific command.",
        "examples": ["help", "help send"],
    },
}


def cmd_help(store: Store, cmd: ParsedCommand):
    target = cmd.args[0].lower() if cmd.args else None

    if target and target in HELP:
        h = HELP[target]
        console.print(f"\n  [cmd]{target}[/cmd]")
        console.print(f"  [muted]{h['desc']}[/muted]\n")
        console.print(f"  [dim]usage[/dim]")
        console.print(f"  [flag]{h['usage']}[/flag]\n")
        console.print(f"  [dim]examples[/dim]")
        for ex in h["examples"]:
            console.print(f"  [muted]$[/muted] [val]{ex}[/val]")
        console.print()
    elif target:
        console.print(f"  [muted]unknown command '{target}' — try [/muted][cmd]help[/cmd]")
    else:
        console.print(f"\n  [dim]{'cmd':<14}{'usage':<45}[/dim]")
        console.print(f"  [muted]{'-' * 58}[/muted]")
        for name, h in HELP.items():
            console.print(f"  [cmd]{name:<14}[/cmd][muted]{h['usage']}[/muted]")
        console.print(f"\n  [dim]type [/dim][cmd]help <cmd>[/cmd][dim] for details[/dim]\n")

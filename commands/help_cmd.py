from core.display import console
from core.parser import ParsedCommand
from core.store import Store

HELP: dict[str, dict] = {
    "bal": {
        "usage": "bal [--acct <checking|savings>]",
        "desc":  "Show depository account balances and current-month spending summary.",
        "examples": ["bal", "bal --acct savings"],
    },
    "send": {
        "usage": "send <amt> to <user> [--memo <text>] [--recurring]",
        "desc":  "Send money to a contact. Prompts for confirmation.",
        "examples": ["send 58 to @maya --memo 'rent'", "send 100 to @jay --recurring"],
    },
    "transfer": {
        "usage": "transfer <amt> to <savings|checking>",
        "desc":  "Move money between your own accounts.",
        "examples": ["transfer 500 to savings", "transfer 200 to checking"],
    },
    "tx": {
        "usage": "tx [--last <n>] [--acct <type|name>] [| grep <term>]",
        "desc":  "List transactions with category tags. Use --acct for any account.",
        "examples": ["tx --last 10", "tx --acct 'amex gold'", "tx --last 30 | grep amazon"],
    },
    "spend": {
        "usage": "spend [--month <mon>] [--top <n>]",
        "desc":  "Spending breakdown by merchant and category.",
        "examples": ["spend", "spend --month may", "spend --top 10"],
    },
    "budget": {
        "usage": "budget [--month <mon>]",
        "desc":  "Category spending vs. set limits with progress bars.",
        "examples": ["budget", "budget --month may"],
    },
    "statement": {
        "usage": "statement [--month <mon>] [--format <text|csv>]",
        "desc":  "Monthly statement. Pass --format csv to save a file.",
        "examples": ["statement --month jun", "statement --month may --format csv"],
    },
    "contacts": {
        "usage": "contacts [<search>]",
        "desc":  "List contacts, or search by name / username.",
        "examples": ["contacts", "contacts maya"],
    },
    "recurring": {
        "usage": "recurring",
        "desc":  "Show active recurring payments and their next dates.",
        "examples": ["recurring"],
    },
    "cards": {
        "usage": "cards",
        "desc":  "Show all cards and their current status.",
        "examples": ["cards"],
    },
    "freeze": {
        "usage": "freeze card",
        "desc":  "Immediately freeze your debit card.",
        "examples": ["freeze card"],
    },
    "unfreeze": {
        "usage": "unfreeze card",
        "desc":  "Reactivate a frozen card.",
        "examples": ["unfreeze card"],
    },
    "banks": {
        "usage": "banks",
        "desc":  "Show all linked institutions with accounts and balances grouped by bank.",
        "examples": ["banks"],
    },
    "credit": {
        "usage": "credit",
        "desc":  "Credit card overview: balances, utilization bars, due dates, APR.",
        "examples": ["credit"],
    },
    "networth": {
        "usage": "networth  (alias: nw)",
        "desc":  "Assets vs liabilities breakdown with 6-month trend sparkline.",
        "examples": ["networth", "nw"],
    },
    "portfolio": {
        "usage": "portfolio [--acct <brokerage|roth>]  (alias: port)",
        "desc":  "Investment holdings with P&L, allocation bars, and sparklines.",
        "examples": ["portfolio", "port --acct roth"],
    },
    "quote": {
        "usage": "quote <TICKER> [TICKER ...]",
        "desc":  "Live quote with sparkline, 52-week range, and your position if held.",
        "examples": ["quote AAPL", "quote VTI FSKAX MSFT"],
    },
    "chart": {
        "usage": "chart [--spend | --balance [--acct <type>] | --networth] [--months N]",
        "desc":  "ASCII charts: spending bars, balance line chart, or net worth trend.",
        "examples": [
            "chart --spend",
            "chart --balance --acct savings",
            "chart --networth --months 6",
        ],
    },
    "help": {
        "usage": "help [<cmd>]",
        "desc":  "Show this overview, or detailed help for one command.",
        "examples": ["help", "help send", "help portfolio"],
    },
}

GROUPS = {
    "accounts":    ["bal", "banks", "cards", "transfer"],
    "money":       ["send", "recurring"],
    "history":     ["tx", "spend", "budget", "statement"],
    "credit":      ["credit"],
    "invest":      ["portfolio", "quote", "networth"],
    "charts":      ["chart"],
    "people":      ["contacts"],
    "other":       ["freeze", "unfreeze", "help"],
}


def cmd_help(store: Store, cmd: ParsedCommand):
    target = cmd.args[0].lower() if cmd.args else None

    if target and target in HELP:
        h = HELP[target]
        console.print(f"\n  [cmd]{target}[/cmd]  [muted]{h['desc']}[/muted]")
        console.print(f"\n  [dim]usage[/dim]")
        console.print(f"  [flag]{h['usage']}[/flag]\n")
        console.print(f"  [dim]examples[/dim]")
        for ex in h["examples"]:
            console.print(f"  [muted]$[/muted] [val]{ex}[/val]")
        console.print()

    elif target:
        console.print(f"  [muted]unknown command '{target}'[/muted]")

    else:
        console.print()
        for group, cmds in GROUPS.items():
            console.print(f"  [dim]{group}[/dim]")
            for name in cmds:
                h = HELP[name]
                console.print(f"  [cmd]{name:<14}[/cmd][muted]{h['usage']}[/muted]")
            console.print()
        console.print(f"  [dim]type [/dim][flag]help <cmd>[/flag][dim] for details and examples[/dim]\n")

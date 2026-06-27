from .bal import cmd_bal
from .send import cmd_send
from .transfer import cmd_transfer
from .tx import cmd_tx
from .spend import cmd_spend
from .budget import cmd_budget
from .statement import cmd_statement
from .contacts import cmd_contacts
from .recurring import cmd_recurring
from .cards import cmd_cards
from .freeze import cmd_freeze
from .banks import cmd_banks
from .credit import cmd_credit
from .networth import cmd_networth
from .portfolio import cmd_portfolio
from .quote import cmd_quote
from .chart import cmd_chart
from .help_cmd import cmd_help

COMMANDS = {
    "bal":       cmd_bal,
    "send":      cmd_send,
    "transfer":  cmd_transfer,
    "tx":        cmd_tx,
    "spend":     cmd_spend,
    "budget":    cmd_budget,
    "statement": cmd_statement,
    "contacts":  cmd_contacts,
    "recurring": cmd_recurring,
    "cards":     cmd_cards,
    "freeze":    cmd_freeze,
    "unfreeze":  cmd_freeze,
    "banks":     cmd_banks,
    "credit":    cmd_credit,
    "networth":  cmd_networth,
    "nw":        cmd_networth,
    "portfolio": cmd_portfolio,
    "port":      cmd_portfolio,
    "quote":     cmd_quote,
    "chart":     cmd_chart,
    "help":      cmd_help,
}

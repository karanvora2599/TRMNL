from .bal import cmd_bal
from .send import cmd_send
from .tx import cmd_tx
from .statement import cmd_statement
from .freeze import cmd_freeze
from .help_cmd import cmd_help

COMMANDS = {
    "bal":       cmd_bal,
    "send":      cmd_send,
    "tx":        cmd_tx,
    "statement": cmd_statement,
    "freeze":    cmd_freeze,
    "unfreeze":  cmd_freeze,
    "help":      cmd_help,
}

from core.display import console, bar, error
from core.parser import ParsedCommand
from core.store import Store


def cmd_credit(store: Store, cmd: ParsedCommand):
    accounts = store.get_accounts_by_category("credit")
    if not accounts:
        error("no credit accounts found")
        return

    console.print()
    total_owed = 0.0
    total_limit = 0.0

    for a in accounts:
        inst = store.get_institution(a.get("institution_id", ""))
        inst_name = inst["short_name"] if inst else ""
        nick = a.get("nickname", a.get("type", ""))
        last4 = a.get("last4", "????")
        owed = a.get("balance_owed", 0.0)
        stmt_bal = a.get("statement_balance", 0.0)
        limit = a.get("credit_limit", 0.0)
        min_pay = a.get("minimum_payment", 0.0)
        due = a.get("due_date", "")
        apr = a.get("apr", 0.0)
        util = owed / limit if limit else 0.0
        total_owed += owed
        total_limit += limit

        if util < 0.30:
            util_style = "val"
        elif util < 0.60:
            util_style = "user"
        else:
            util_style = "cmd"

        console.print(
            f"  [val]{nick}[/val]  [dim]{inst_name} ....{last4}[/dim]"
            f"  [muted]APR {apr*100:.2f}%[/muted]"
        )
        console.print(
            f"  [dim]  current balance [/dim][{util_style}]${owed:,.2f}[/{util_style}]"
            f"  [dim]statement [/dim][muted]${stmt_bal:,.2f}[/muted]"
            f"  [dim]limit [/dim][muted]${limit:,.0f}[/muted]"
        )
        util_bar = bar(util, width=24)
        console.print(f"  [{util_style}]  {util_bar}[/{util_style}]  [dim]{util*100:.1f}% utilized[/dim]")
        console.print(
            f"  [dim]  min payment [/dim][cmd]${min_pay:,.2f}[/cmd]"
            f"  [dim]due [/dim][flag]{due}[/flag]"
        )
        console.print()

    if len(accounts) > 1:
        total_util = total_owed / total_limit if total_limit else 0.0
        if total_util < 0.30:
            t_style = "val"
        elif total_util < 0.60:
            t_style = "user"
        else:
            t_style = "cmd"
        console.print(
            f"  [dim]total owed [/dim][{t_style}]${total_owed:,.2f}[/{t_style}]"
            f"  [dim]of ${total_limit:,.0f} combined limit  ({total_util*100:.1f}%)[/dim]"
        )
        console.print()

from core.display import console, error
from core.parser import ParsedCommand
from core.store import Store


def cmd_banks(store: Store, cmd: ParsedCommand):
    institutions = store.get_institutions()
    if not institutions:
        error("no institutions found")
        return

    console.print()
    for inst in institutions:
        accounts = store.get_accounts_by_institution(inst["id"])
        console.print(f"  [val]{inst['name']}[/val]  [dim]{inst['short_name']}[/dim]")

        for a in accounts:
            cat = a.get("account_category", "")
            nick = a.get("nickname") or a.get("type", "")
            last4 = a.get("last4") or a.get("account_number_last4", "????")

            if cat == "depository":
                balance = a.get("balance", 0.0)
                avail = a.get("available_balance", balance)
                avail_str = f"  [dim]avail ${avail:,.2f}[/dim]" if avail != balance else ""
                console.print(
                    f"    [muted]{nick:<18} ....{last4}[/muted]"
                    f"  [val]${balance:>11,.2f}[/val]{avail_str}"
                )
            elif cat == "credit":
                owed = a.get("balance_owed", 0.0)
                limit = a.get("credit_limit", 0.0)
                util = owed / limit if limit else 0.0
                if util < 0.30:
                    util_style = "val"
                elif util < 0.60:
                    util_style = "user"
                else:
                    util_style = "cmd"
                console.print(
                    f"    [muted]{nick:<18} ....{last4}[/muted]"
                    f"  [{util_style}]-${owed:>10,.2f}[/{util_style}]"
                    f"  [dim]/ ${limit:,.0f} limit[/dim]"
                )
            elif cat == "investment":
                value = store.compute_account_market_value(a["id"])
                console.print(
                    f"    [muted]{nick:<18}[/muted]"
                    f"  [flag]${value:>11,.2f}[/flag]  [dim]market value[/dim]"
                )
            elif cat == "loan":
                balance = a.get("current_balance", 0.0)
                original = a.get("original_balance", 0.0)
                pct_paid = (1 - balance / original) * 100 if original else 0
                console.print(
                    f"    [muted]{nick:<18}[/muted]"
                    f"  [cmd]-${balance:>10,.2f}[/cmd]"
                    f"  [dim]{pct_paid:.0f}% paid[/dim]"
                )
        console.print()

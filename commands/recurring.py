from datetime import datetime

from core.display import console, info
from core.parser import ParsedCommand
from core.store import Store


def cmd_recurring(store: Store, cmd: ParsedCommand):
    recs = [r for r in store.get_recurring() if r["status"] == "active"]

    if not recs:
        info("no active recurring payments")
        return

    total = sum(r["amount"] for r in recs)
    console.print()

    for r in recs:
        payee = f"@{r['payee_username']}" if r.get("payee_username") else r["payee_display_name"]
        next_dt = datetime.strptime(r["next_date"], "%Y-%m-%d").strftime("%b %d")
        memo = f"  [dim]{r['memo']}[/dim]" if r.get("memo") else ""
        console.print(
            f"  [user]{payee:<18}[/user]"
            f"  [cmd]-${r['amount']:>8,.2f}[/cmd]"
            f"  [muted]{r['frequency']:<10}[/muted]"
            f"  [dim]next {next_dt}[/dim]"
            f"{memo}"
        )

    console.print(f"\n  [dim]monthly total[/dim]  [cmd]-${total:,.2f}[/cmd]\n")

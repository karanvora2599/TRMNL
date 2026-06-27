from datetime import datetime

from core.display import console, fmt_amount, fmt_date, error, info
from core.parser import ParsedCommand
from core.store import Store

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def cmd_statement(store: Store, cmd: ParsedCommand):
    month_raw = cmd.flags.get("month")
    fmt = str(cmd.flags.get("format", "text")).lower()

    now = datetime.now()
    if month_raw:
        m_lower = str(month_raw).lower()
        if m_lower in MONTH_NAMES:
            month = MONTH_NAMES[m_lower]
        else:
            try:
                month = int(month_raw)
            except ValueError:
                error(f"unrecognised month '{month_raw}' -- try jan, feb, ..., dec")
                return
    else:
        month = now.month

    year = int(cmd.flags.get("year", now.year))

    acct = store.get_default_account()
    txns = store.get_transactions(account_id=acct["id"], month=month, year=year)

    month_name = datetime(year, month, 1).strftime("%B %Y")

    if not txns:
        info(f"no transactions found for {month_name}")
        return

    total_in = sum(t["amount"] for t in txns if t["type"] == "credit")
    total_out = sum(t["amount"] for t in txns if t["type"] != "credit")
    net = total_in - total_out

    sep = "-" * 52
    console.print(f"\n  [muted]{sep}[/muted]")
    console.print(f"  [brand]STATEMENT[/brand]  [muted]{month_name}  /  {acct['type']} ....{acct['account_number_last4']}[/muted]")
    console.print(f"  [muted]{sep}[/muted]\n")

    for t in reversed(txns):
        date = fmt_date(t["created_at"])
        name = t["merchant"]["name"]
        memo = f"  [dim]{t['memo']}[/dim]" if t.get("memo") else ""
        amount = fmt_amount(t["amount"], t["type"])
        console.print(f"  [muted]{date}[/muted]  {name:<28}{amount}{memo}")

    console.print(f"\n  [muted]{sep}[/muted]")
    console.print(f"  [muted]{'money in':<20}[/muted][val]+${total_in:>10,.2f}[/val]")
    console.print(f"  [muted]{'money out':<20}[/muted][cmd]-${total_out:>10,.2f}[/cmd]")
    net_color = "val" if net >= 0 else "cmd"
    net_sign = "+" if net >= 0 else "-"
    console.print(f"  [muted]{'net':<20}[/muted][{net_color}]{net_sign}${abs(net):>10,.2f}[/{net_color}]")
    console.print(f"  [muted]{sep}[/muted]\n")

    if fmt in ("csv", "txt"):
        _save_statement(txns, month_name, net, fmt)


def _save_statement(txns, month_name, net, fmt):
    filename = f"statement_{month_name.replace(' ', '_').lower()}.{fmt}"
    if fmt == "csv":
        lines = ["date,merchant,category,type,amount,memo,status"]
        for t in reversed(txns):
            date = fmt_date(t["created_at"])
            sign = "" if t["type"] == "credit" else "-"
            lines.append(
                f"{date},{t['merchant']['name']},{t['merchant']['category']},"
                f"{t['type']},{sign}{t['amount']},{t.get('memo') or ''},{t['status']}"
            )
    else:
        lines = [f"STATEMENT - {month_name}", ""]
        for t in reversed(txns):
            date = fmt_date(t["created_at"])
            sign = "+" if t["type"] == "credit" else "-"
            lines.append(f"{date}  {t['merchant']['name']:<30} {sign}${t['amount']:,.2f}")
        lines += ["", f"Net: ${net:+,.2f}"]

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    from core.display import info
    info(f"saved -> {filename}")

from core.charts import horizontal_bars, line_chart
from core.display import console, error
from core.parser import ParsedCommand
from core.store import Store


_MONTH_ABBR = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


def _short_month(label: str) -> str:
    """Convert '2026-01' → 'Jan' or pass through short labels."""
    parts = label.split("-")
    if len(parts) == 2 and parts[1] in _MONTH_ABBR:
        return _MONTH_ABBR[parts[1]]
    return label[:4]


def cmd_chart(store: Store, cmd: ParsedCommand):
    months = int(cmd.flags.get("months", 6))  # type: ignore[arg-type]

    if "spend" in cmd.flags:
        _chart_spend(store, months)
    elif "balance" in cmd.flags:
        acct_query = cmd.flags.get("acct")
        _chart_balance(store, months, str(acct_query) if acct_query else None)
    elif "networth" in cmd.flags or "nw" in cmd.flags:
        _chart_networth(store, months)
    else:
        error("usage: chart [--spend | --balance [--acct <type>] | --networth] [--months N]")


def _chart_spend(store: Store, months: int):
    history = store.get_monthly_spend_history()[-months:]
    if not history:
        error("no spending history available")
        return
    console.print()
    console.print(f"  [dim]monthly spending  (last {len(history)} months)[/dim]")
    console.print()
    items = [(_short_month(h["month"]), h["total"]) for h in history]
    for line in horizontal_bars(items, label_width=4, bar_width=28, color="cmd"):
        console.print(line)
    console.print()


def _chart_balance(store: Store, months: int, acct_query: str | None):
    if acct_query:
        acct = store.find_account(acct_query)
        if not acct:
            error(f"no account matching '{acct_query}'")
            return
        acct_id = acct["id"]
        title = acct.get("nickname") or acct.get("type", acct_query)
    else:
        acct = store.get_default_account()
        acct_id = acct["id"]
        title = acct.get("type", "checking")

    history = store.get_balance_history(account_id=acct_id)[-months:]
    if not history:
        error("no balance history available")
        return

    labels = [_short_month(h["month"]) for h in history]
    values = [h["balance"] for h in history]

    console.print()
    console.print(f"  [dim]{title} balance  (last {len(history)} months)[/dim]")
    console.print()
    for line in line_chart(labels, values, height=7, col_width=6, color="val"):
        console.print(line)
    console.print()


def _chart_networth(store: Store, months: int):
    history = store.get_net_worth_history()[-months:]
    if not history:
        error("no net worth history available")
        return

    labels = [_short_month(h["month"]) for h in history]
    values = [h["net_worth"] for h in history]

    console.print()
    console.print(f"  [dim]net worth  (last {len(history)} months)[/dim]")
    console.print()
    for line in line_chart(labels, values, height=7, col_width=6, color="flag"):
        console.print(line)
    console.print()

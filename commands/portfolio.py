from core.charts import sparkline, horizontal_bars
from core.display import console, bar, error
from core.parser import ParsedCommand
from core.store import Store


_ASSET_CLASS_STYLE = {
    "equity": "flag",
    "etf": "val",
    "mutual_fund": "teal",
    "bond": "user",
}


def cmd_portfolio(store: Store, cmd: ParsedCommand):
    acct_query = cmd.flags.get("acct")

    if acct_query:
        acct = store.find_account(str(acct_query))
        if not acct:
            error(f"no investment account matching '{acct_query}'")
            return
        accounts = [acct]
    else:
        accounts = store.get_accounts_by_category("investment")

    if not accounts:
        error("no investment accounts found")
        return

    console.print()
    grand_total = 0.0
    grand_cost = 0.0

    for acct in accounts:
        holdings = store.get_holdings(account_id=acct["id"])
        if not holdings:
            continue

        acct_value = store.compute_account_market_value(acct["id"])
        grand_total += acct_value

        nick = acct.get("nickname", acct.get("type", ""))
        inst = store.get_institution(acct.get("institution_id", ""))
        inst_name = inst["short_name"] if inst else ""
        console.print(f"  [val]{nick}[/val]  [dim]{inst_name}[/dim]  [val]${acct_value:,.2f}[/val]")

        for h in holdings:
            q = store.get_quote(h["ticker"])
            if not q:
                continue
            value = store.compute_holding_value(h)
            gain, gain_pct = store.compute_holding_gain(h)
            cost = h["shares"] * h["cost_basis_per_share"]
            grand_cost += cost
            style = "val" if gain >= 0 else "cmd"
            sign = "+" if gain >= 0 else ""
            asset_style = _ASSET_CLASS_STYLE.get(h.get("asset_class", ""), "muted")
            alloc_frac = value / acct_value if acct_value else 0
            alloc_bar = bar(alloc_frac, width=12)
            spark = sparkline(q.get("price_history", []))
            console.print(
                f"  [muted]  {h['ticker']:<6}[/muted]"
                f"  [dim]{h['name']:<24}[/dim]"
                f"  [{asset_style}]{h.get('asset_class',''):<12}[/{asset_style}]"
                f"  [val]${value:>9,.2f}[/val]"
                f"  [{style}]{sign}${gain:,.2f} ({sign}{gain_pct*100:.1f}%)[/{style}]"
            )
            console.print(
                f"  [muted]  {'':<6}  {h['shares']:.4f} sh  "
                f"@ ${q['current_price']:.2f}  basis ${h['cost_basis_per_share']:.2f}[/muted]"
                f"  [dim]{alloc_bar} {alloc_frac*100:.1f}%[/dim]"
                f"  [dim]{spark}[/dim]"
            )
        console.print()

    if len(accounts) > 1 and grand_total > 0:
        grand_gain = grand_total - grand_cost
        grand_pct = grand_gain / grand_cost if grand_cost else 0
        style = "val" if grand_gain >= 0 else "cmd"
        sign = "+" if grand_gain >= 0 else ""
        console.print(
            f"  [dim]total portfolio[/dim]  [val]${grand_total:,.2f}[/val]"
            f"  [{style}]{sign}${grand_gain:,.2f} ({sign}{grand_pct*100:.1f}%)[/{style}]"
        )

        # Allocation by asset class
        class_totals: dict[str, float] = {}
        for acct in accounts:
            for h in store.get_holdings(account_id=acct["id"]):
                cls = h.get("asset_class", "other")
                class_totals[cls] = class_totals.get(cls, 0.0) + store.compute_holding_value(h)
        if class_totals:
            console.print()
            console.print(f"  [dim]allocation[/dim]")
            items = sorted(class_totals.items(), key=lambda x: x[1], reverse=True)
            for line in horizontal_bars(items, label_width=12, bar_width=16, color="flag"):
                console.print(line)
        console.print()

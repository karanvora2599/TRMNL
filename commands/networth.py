from core.display import console, bar
from core.parser import ParsedCommand
from core.store import Store


def cmd_networth(store: Store, cmd: ParsedCommand):
    nw = store.compute_net_worth()
    history = store.get_net_worth_history()

    console.print()
    console.print(f"  [dim]net worth[/dim]  [val]${nw['net_worth']:,.2f}[/val]")
    console.print()

    # Assets
    console.print(f"  [dim]assets[/dim]  [val]${nw['assets']:,.2f}[/val]")
    console.print(
        f"  [muted]  cash & savings  [/muted][val]${nw['depository']:>12,.2f}[/val]"
    )
    console.print(
        f"  [muted]  investments     [/muted][flag]${nw['investments']:>12,.2f}[/flag]"
    )

    max_asset = max(nw["depository"], nw["investments"]) or 1
    dep_bar = bar(nw["depository"] / max_asset, width=20)
    inv_bar = bar(nw["investments"] / max_asset, width=20)
    console.print(f"  [val]  {dep_bar}[/val]  [dim]cash[/dim]")
    console.print(f"  [flag]  {inv_bar}[/flag]  [dim]investments[/dim]")
    console.print()

    # Liabilities
    console.print(f"  [dim]liabilities[/dim]  [cmd]-${nw['liabilities']:,.2f}[/cmd]")
    console.print(
        f"  [muted]  credit cards    [/muted][cmd]-${nw['credit_owed']:>11,.2f}[/cmd]"
    )
    console.print(
        f"  [muted]  loans           [/muted][cmd]-${nw['loans']:>11,.2f}[/cmd]"
    )

    max_liab = max(nw["credit_owed"], nw["loans"]) or 1
    cc_bar = bar(nw["credit_owed"] / max_liab, width=20)
    ln_bar = bar(nw["loans"] / max_liab, width=20)
    console.print(f"  [cmd]  {cc_bar}[/cmd]  [dim]credit cards[/dim]")
    console.print(f"  [cmd]  {ln_bar}[/cmd]  [dim]loans[/dim]")
    console.print()

    if history:
        from core.charts import sparkline
        vals = [h["net_worth"] for h in history]
        spark = sparkline(vals)
        first = history[0]
        last = history[-1]
        change = last["net_worth"] - first["net_worth"]
        sign = "+" if change >= 0 else ""
        style = "val" if change >= 0 else "cmd"
        console.print(
            f"  [dim]6-month trend[/dim]  [{style}]{spark}[/{style}]"
            f"  [{style}]{sign}${change:,.2f}[/{style}]"
            f"  [dim]({history[0]['month']} - {history[-1]['month']})[/dim]"
        )
        console.print()

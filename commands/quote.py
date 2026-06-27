from core.charts import sparkline
from core.display import console, error
from core.parser import ParsedCommand
from core.store import Store


def cmd_quote(store: Store, cmd: ParsedCommand):
    tickers = [t.upper() for t in cmd.args]
    if not tickers:
        error("usage: quote <TICKER> [TICKER ...]")
        return

    console.print()
    for ticker in tickers:
        q = store.get_quote(ticker)
        if not q:
            console.print(f"  [muted]no quote for {ticker}[/muted]")
            continue

        day_chg = q.get("day_change", 0.0)
        day_pct = q.get("day_change_pct", 0.0)
        style = "val" if day_chg >= 0 else "cmd"
        sign = "+" if day_chg >= 0 else ""

        spark = sparkline(q.get("price_history", []))

        console.print(
            f"  [flag]{q['ticker']}[/flag]  [dim]{q['name']}[/dim]"
            f"  [val]${q['current_price']:.2f}[/val]"
            f"  [{style}]{sign}{day_chg:.2f} ({sign}{day_pct*100:.2f}%)[/{style}]"
        )
        console.print(
            f"  [muted]  prev close ${q['prev_close']:.2f}"
            f"  52w {q['week_52_low']:.2f} - {q['week_52_high']:.2f}"
            f"  mkt cap {q.get('market_cap','N/A')}"
            f"[/muted]"
        )
        console.print(f"  [dim]  {spark}[/dim]  [muted]9-session trend[/muted]")

        # Show user's position if held
        all_holdings = store.get_holdings()
        my = [h for h in all_holdings if h["ticker"] == ticker]
        if my:
            for h in my:
                acct = store.find_account(h["account_id"])
                acct_name = acct.get("nickname", h["account_id"]) if acct else h["account_id"]
                value = store.compute_holding_value(h)
                gain, gain_pct = store.compute_holding_gain(h)
                g_style = "val" if gain >= 0 else "cmd"
                g_sign = "+" if gain >= 0 else ""
                console.print(
                    f"  [dim]  your position [{acct_name}][/dim]"
                    f"  [muted]{h['shares']:.4f} sh[/muted]"
                    f"  [flag]${value:,.2f}[/flag]"
                    f"  [{g_style}]{g_sign}${gain:,.2f} ({g_sign}{gain_pct*100:.1f}%)[/{g_style}]"
                )
        console.print()

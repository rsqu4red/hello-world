#!/usr/bin/env python3
"""
DLDR — "Day Late, Dollar Richer" — FAITHFUL backtest.
Source: Bezdjian, "Am I the Patsy?" (SSRN 5360727) and SSRN 5400451.

This is the implementation that actually matches the papers, because it uses the
real signal — daily change in SHARES OUTSTANDING — which TradingView cannot
provide. Feed it a CSV with daily NAV and shares outstanding for an LETF.

Signal (T+1 execution):
    dShares = shares[t] - shares[t-1]
    dShares > 0 (creation)   -> SHORT k*dShares  shares at NAV[t+1]
    dShares < 0 (redemption) -> BUY   k*|dShares| shares at NAV[t+1]
FIFO covering, daily mark-to-market on the residual at the end.

CSV format (header required), one row per trading day, ascending by date:
    date,nav,shares_outstanding
    2015-01-02,12.34,15000000
    ...
'shares_outstanding' should be the ACTUAL share count (the papers report issuer
figures in thousands — multiply by 1000 if your source is in thousands).

Usage:
    python dldr_backtest.py SQQQ.csv --scale 1e-5 --borrow 0.08
"""
import argparse
import csv
from collections import deque


def load(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"], float(r["nav"]), float(r["shares_outstanding"])))
    rows.sort(key=lambda x: x[0])
    return rows


def run(rows, scale, borrow_apr):
    """FIFO P&L of trading k*dShares one day late at NAV. Returns metrics."""
    lots = deque()          # signed lots: (+qty long / -qty short, entry_nav)
    realized = 0.0
    borrow_cost = 0.0
    daily_pnl = []
    equity = 0.0

    for i in range(1, len(rows) - 1):
        d_shares = rows[i][2] - rows[i - 1][2]
        if d_shares == 0:
            continue
        exec_nav = rows[i + 1][1]            # T+1 NAV
        # creation -> short (negative qty) ; redemption -> long (positive qty)
        qty = -scale * d_shares
        side = 1 if qty > 0 else -1          # +1 long, -1 short
        remaining = abs(qty)

        # FIFO close opposing lots first
        while remaining > 1e-12 and lots and (lots[0][0] > 0) != (side > 0):
            lot_qty, lot_nav = lots[0]
            close_qty = min(remaining, abs(lot_qty))
            # P&L: long lot profits when nav rises; short lot profits when nav falls
            if lot_qty > 0:
                realized += close_qty * (exec_nav - lot_nav)
            else:
                realized += close_qty * (lot_nav - exec_nav)
            remaining -= close_qty
            if abs(lot_qty) - close_qty < 1e-12:
                lots.popleft()
            else:
                # shrink the opposing lot toward zero (closing reduces magnitude)
                lots[0] = (lot_qty + side * close_qty, lot_nav)
        # any excess opens a new lot in the signal direction
        if remaining > 1e-12:
            lots.append((side * remaining, exec_nav))

        # daily borrow accrual on net short notional
        net = sum(q for q, _ in lots)
        short_notional = sum(abs(q) * exec_nav for q, _ in lots if q < 0)
        borrow_cost += short_notional * borrow_apr / 252.0

        mtm = sum((q * (exec_nav - nav)) for q, nav in lots)   # signed
        equity = realized + mtm - borrow_cost
        daily_pnl.append(equity - (daily_pnl[-1] if daily_pnl else 0.0))

    # final mark
    last_nav = rows[-1][1]
    mtm = sum(q * (last_nav - nav) for q, nav in lots)
    total = realized + mtm - borrow_cost
    return {
        "realized": realized,
        "final_mtm": mtm,
        "borrow_cost": borrow_cost,
        "total_pnl": total,
        "days": len(rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--scale", type=float, default=1e-5,
                    help="Fraction of issuer share delta to trade (paper uses 1/100000=1e-5)")
    ap.add_argument("--borrow", type=float, default=0.08,
                    help="Annual borrow cost on short notional (decimal)")
    args = ap.parse_args()
    rows = load(args.csv)
    res = run(rows, args.scale, args.borrow)
    print(f"Rows: {res['days']}")
    print(f"Realized P&L:        ${res['realized']:,.2f}")
    print(f"Final mark-to-market:${res['final_mtm']:,.2f}")
    print(f"Borrow cost charged: ${res['borrow_cost']:,.2f}")
    print(f"TOTAL P&L:           ${res['total_pnl']:,.2f}")
    print("\nNOTE: capital-at-risk varies daily, so a single CAGR/Sharpe is "
          "misleading (the papers concede this). Compare total P&L to average "
          "notional deployed, and re-run across many tickers before concluding.")


if __name__ == "__main__":
    main()

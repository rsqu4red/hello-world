# Handsome Rob 1:1.5 — TradingView Strategy

Pine Script v5 implementation of the strategy from:

> Bezdjian, R. "Deception by Design: Leveraged ETFs, Structural Fraud, and Proof of Outperformance" (SSRN 5347238, Jul 2025)

## The Idea (1 paragraph)

Leveraged and inverse ETFs (TQQQ/SQQQ, SOXL/SOXS, FAS/FAZ, …) lose value to compounding/volatility decay every day they are held. The two sides of a pair are **not** true opposites — the issuer's own prospectus performance tables show inverse legs decay faster. Shorting **both** legs at a 1:1.5 (long:inverse) notional ratio, quarterly rebalanced, with a "top-up" rule whenever either leg falls 10%, captures that decay as alpha with low beta to the S&P 500.

Reported aggregate backtest in the paper: **~19.6 % CAGR, ~5.5 % qtr vol, −11.1 % max DD, β 0.37, α +6.2 %/yr** vs S&P 500.

## Deploying on TradingView

1. Open the chart of a **long** leveraged ETF (e.g. `AMEX:TQQQ`, `AMEX:SOXL`, `AMEX:FAS`).
2. Open Pine Editor → paste `handsome_rob_strategy.pine` → **Save** → **Add to chart**.
3. Settings → set **Inverse LETF symbol** to the matching pair (`SQQQ`, `SOXS`, `FAZ`, …).
4. Use the **Strategy Tester** panel to view P&L, drawdown, list of trades.

The chart symbol short is placed as real orders; the inverse leg is tracked synthetically and folded into the **Synthetic Combined Equity** plot, which is the curve you should read for the full two-leg strategy.

## Pairs that worked best in the paper

| Pair | Total Return | Win Rate | Beta | Alpha (ann.) |
|---|---|---|---|---|
| JNUG / JDST | 6,479% | 78% | -0.09 | 4.24% |
| SOXL / SOXS | 4,602% | 88% | 0.11 | 2.36% |
| FAS  / FAZ  | 3,874% | 83% | 0.07 | 2.78% |
| TECL / TECS | 1,547% | 89% | 0.21 | 2.27% |
| TNA  / TZA  | 1,328% | 88% | 0.53 | 0.91% |

GUSH / DRIP is the only loser — the paper still shows positive alpha there.

## Risk controls in this implementation

| Control | Default | Purpose |
|---|---|---|
| Per-leg top-up cap | 20 / quarter | Stops runaway adds in a sustained rally |
| Per-leg notional ceiling | 5× initial | Caps absolute size grown via top-ups |
| Borrow-fee accrual | 6 % p.a. per leg | Matches paper's avg cost; raise to 15–30 % to stress inverse legs |
| Equity kill switch | 25 % DD from peak | Hard stop on catastrophic move |
| Date filter | off | Walk-forward backtests |

## Caveats — read before risking money

1. **Short borrow is the real-world wildcard.** Inverse LETFs frequently go *hard-to-borrow* (HTB) with fees of 10–50%+ p.a. and forced buy-ins. Stress the borrow input.
2. **Unlimited theoretical loss** on a short leveraged ETF during a sustained rally. The notional ceiling + kill switch mitigate but do not eliminate this.
3. **Dual-leg execution at a broker.** TradingView strategies can only post orders on the chart symbol, so the synthetic equity is your truth source for backtest stats. Live, run two coordinated executions or drive an external system from the alerts included.
4. **Survivorship.** The paper used full-universe data including delisted LETFs. TradingView only carries currently-listed tickers, so your backtest on `SOXL/SOXS` etc. is biased upward versus the paper's universe-level numbers.
5. **Borrow + financing + taxes** can wipe out the alpha shown in raw price-only backtests. The 6% built in is a starting point, not a guarantee.
6. **Not investment advice.** Backtest only. Paper-trade first.

## Files

- `handsome_rob_strategy.pine` — strategy script (Pine v5)
- `HANDSOME_ROB_README.md` — this file

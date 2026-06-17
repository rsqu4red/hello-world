# LETF Strategies — from the Bezdjian SSRN papers

Trading strategies extracted from three working papers by **Rob Bezdjian**, all on
the mechanics of **leveraged & inverse ETFs (LETFs)**:

| # | Paper | SSRN | Core contribution |
|---|-------|------|-------------------|
| 1 | *Deception by Design: Leveraged ETFs, Structural Fraud, and Proof of Outperformance* | 5347238 | **Handsome Rob** (short the pair, harvest decay) + **Jerry Maguire** audit |
| 2 | *Am I the Patsy? LETF Issuance Is Signal, Not Noise* | 5360727 | **DLDR** — trade against issuer share-flow, one day late |
| 3 | *Who's the Dog and Who's the Tail?* | 5400451 | TQQQ event-study; **Creation-Spike Fade**; DLDR in stress windows |

> ⚠️ These are **non-peer-reviewed advocacy / whistleblower papers**, heavy on
> rhetoric ("fraud", "rigged", "Madoff"). The *underlying market phenomenon*
> (volatility decay in daily-reset leveraged ETFs) is real and well documented in
> mainstream academic literature. The *legal/conspiracy framing* is the author's
> contested opinion and is irrelevant to whether the trades make money. This
> README separates the tradeable signal from the narrative. Nothing here is
> investment advice.

---

## The strategies

### Strategy 1 — "Handsome Rob": short the LETF pair, harvest decay
**Files:** `01_handsome_rob_single_leg.pine` (native strategy, one leg) ·
`02_handsome_rob_pair.pine` (synthetic pair equity)

A 3×-long ETF (e.g. TQQQ) and its 3×-inverse twin (SQQQ) both *reset leverage
daily*. In any choppy / mean-reverting tape, daily compounding drags **both**
products lower than a naïve "3× the index" would suggest — the well-known
**volatility decay / beta-slippage**. Handsome Rob shorts **both legs** at a
**1 : 1.5 notional ratio** ($1,000 short the long-LETF, $1,500 short the
inverse), tops up each leg by 10% whenever it falls (adding to the *winning*
short), and resets quarterly.

- **Where it makes money:** range-bound, high-volatility, mean-reverting regimes.
- **Where it bleeds:** strong sustained *trends*. In a long rally the short on
  the long-LETF (TQQQ) has theoretically **unbounded loss**; in a crash the short
  on the inverse (SQQQ) spikes. The "no trimming on the losing leg" rule lets that
  run until quarter-end — the strategy's single biggest risk.
- **Reported (paper):** ~19.6% annualised, beta 0.37, max DD −11.1% across the
  Direxion universe. **Not independently audited; excludes realistic borrow.**

### Strategy 2 — "DLDR" (Day Late, Dollar Richer): fade issuer share-flow
**Files:** `python/dldr_backtest.py` (faithful) · `03_dldr_proxy.pine` (proxy only)

Signal = **daily change in shares outstanding**. Issuer *creates* shares
(ΔShares > 0) → **short** the ETF the next day at NAV. Issuer *redeems*
(ΔShares < 0) → **buy / cover** the next day. The thesis: creations cluster into
weakness and redemptions into strength, so trading *against the flow with a
1-day lag* mirrors the issuer's own edge.

- **Critical limitation:** TradingView has **no shares-outstanding data**, so
  this cannot be back-tested in Pine. Use the **Python script** with issuer CSVs
  (NAV + shares outstanding). The `.pine` file is only a *price-based
  mean-reversion proxy* and is explicitly **not** DLDR.

### Strategy 3 — "Creation-Spike Fade" (CSF)
**File:** `03_dldr_proxy.pine` (CSF gate built in)

A discretised DLDR: when net creations exceed the 90th percentile of a 63-day
window *during a drawdown*, short for H days; redemption spikes during rebounds
trigger a long. Same data limitation as DLDR — the Pine version gates the
price-proxy z-score by a percentile band instead of true flow.

### (Not a strategy) — "Jerry Maguire" audit
A forensic accounting method to estimate issuer profit from creation/redemption
flows. It's an **analytics tool, not a trade**, so there's no Pine code for it.

---

## Ranking — best to worst

| Rank | Strategy | Why |
|------|----------|-----|
| **1** | **Handsome Rob — pair short (02)** | Rests on a *real, documented* effect (decay). Market-neutral-ish by construction (short both sides), lowest directional risk of the set, and is the only one back-testable today without alternative data. Edge is structural, not predictive. |
| **2** | **Handsome Rob — single leg (01)** | Same effect but one-sided, so it carries full directional risk on whichever leg you short. Useful as a building block / for borrow-availability reasons, weaker stand-alone. |
| **3** | **DLDR (Python, faithful)** | *Plausible* contrarian flow signal, but the causal story ("issuer must sell high / redeem low") misunderstands creation-redemption economics (APs transact **at NAV**; issuers earn fees & swap spreads, not NAV arbitrage). Needs alt-data, variable capital-at-risk makes risk metrics unreliable, and the paper's own results show several legs lose money. |
| **4** | **Creation-Spike Fade** | A less-tested discretisation of DLDR; more parameters, same data problem, no independent validation. |
| **5** | **DLDR / CSF price proxy (03 Pine)** | Honest fallback, but it is **not** the paper's strategy — it degenerates into ordinary mean-reversion. Use only as a sanity check. |

---

## Neutral scientific view

**What is solidly true.** Daily-rebalanced leveraged ETFs *do* suffer
path-dependent volatility decay. This is textbook (Cheng & Madhavan 2009;
Avellaneda & Zhang 2010) — not a discovery and not, by itself, fraud. Shorting
both legs of a leveraged pair to harvest that decay is a known, legitimate trade.

**What the papers overstate or get wrong.**
- **Borrow cost & availability.** The decay edge is routinely *eaten* by
  stock-borrow fees. Inverse and volatility LETFs are often hard-to-borrow with
  fees well above the author's assumed ~6–8%/yr — sometimes 20–100%+ annualised,
  or simply unavailable. The headline returns appear to ignore this.
- **Tail / trend risk.** Shorting both legs is short-gamma-like: small steady
  gains in chop, occasional large losses in trends. The "never trim the loser"
  rule and quarterly-reset cadence concentrate that risk. Reported max-DD of
  −11% is implausibly mild for a levered short book through 2020/2022.
- **Survivorship & reverse splits.** LETFs are delisted, reverse-split, and
  relaunched under reused tickers/new CUSIPs (the author admits this). Backtests
  spanning "inception to present" across "every pair" are very exposed to
  survivorship bias unless point-in-time data is used.
- **The flow-causality claim (DLDR) is the weakest link.** Creation/redemption
  is an arbitrage mechanism that keeps **price ≈ NAV**; APs transact at NAV and
  do not profit from "selling high, redeeming low." Issuer profit comes from
  management fees and swap spreads. So "ΔShares is a profit footprint" conflates
  a *hedging/lagging* response to investor demand with a *predictive* edge. Any
  real DLDR alpha is more likely short-horizon **mean reversion** than a
  guaranteed structural transfer.
- **Capacity & extrapolation.** Scaling a 1/100,000 sleeve "× 100,000 ⇒ $28.8B"
  is not legitimate — it ignores market impact, borrow capacity, and that you'd
  *be* the flow you're trading against.
- **Metrics.** The papers concede DLDR's capital-at-risk varies daily, which
  makes the quoted CAGR/Sharpe/Sortino unreliable; total-$ P&L is the only clean
  figure, and several legs (KOLD, UCO, SCO, SVXY) lost money.

**Bottom line.** There is a genuine, exploitable inefficiency here — **leveraged-ETF
volatility decay** — best expressed as the market-neutral pair short (Strategy 1).
Treat the rest as hypotheses requiring your own out-of-sample, cost-inclusive
validation. Before risking capital: (1) model real borrow fees and HTB
availability, (2) stress-test through 2008/2020/2022 trends, (3) use point-in-time
data to kill survivorship bias, (4) cap per-leg loss (the paper's design does
not). The fraud/legal claims are unproven opinion and should not factor into the
trading decision.

---

## How to back-test

**Pine (TradingView):** open the `.pine` files in Pine Editor, "Add to chart."
- `01` and `03` are `strategy{}` scripts → use the **Strategy Tester** tab.
- `02` is an `indicator{}` → it plots the synthetic combined-pair equity curve.
- In Strategy Properties set realistic **commission + slippage**, and remember
  Pine still won't charge real **borrow** — use the modelled-borrow inputs and
  treat results as optimistic.

**Python (faithful DLDR):**
```bash
python python/dldr_backtest.py SQQQ.csv --scale 1e-5 --borrow 0.08
```
CSV needs `date,nav,shares_outstanding` (actual share count — multiply by 1000 if
your source reports thousands). Source NAV/shares from the issuer (ProShares,
Direxion) daily files.

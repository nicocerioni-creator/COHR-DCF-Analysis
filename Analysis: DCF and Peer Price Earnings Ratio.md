# Analysis: DCF and Peer Price Earnings Ratio

Target: Coherent Corp. (NYSE: COHR). Comparison date: September 15, 2026. Review prepared September 17, 2026. All valuation results below are USD per COHR common share, using the models' stated dilution conventions.

| Method | Your company's result and date | Main assumption or limitation |
|---|---|---|
| Week 3 DCF | **$42.28–$84.03 sensitivity range; $57.20 base case.** September 15, 2026 comparison, reproduced by running the saved `dcf.py` on September 17, 2026. | Holds the FY2027–FY2031 cash-flow forecast and equity bridge fixed while testing WACC of 9%–11% and terminal growth of 2%–4%. Base WACC of 10% is explicitly an unresolved training placeholder. This is the saved model's tested range, not a confidence interval or a full range of operating scenarios. |
| Peer P/E | **$118.36 single-peer reference; no peer range.** September 15, 2026 closing prices and annual reported diluted EPS public by that date. | Fabrinet supplies the only usable multiple: $374.91 / $13.05 = 28.728736x, applied to COHR's $4.12 EPS. FN's contract-manufacturing model limits comparability. LITE's negative annual EPS excludes it from the calculation. Remaining policy-evidence gaps keep the reference conditional. |

The saved COHR market-price benchmark is **$271.17 on September 15, 2026**. Both model results are below that benchmark, but this does not establish that the market is wrong. The methods are not averaged, and the gap between them is not presented as a new valuation range.

## Reproduced DCF evidence

Command executed from the repository root: `python3 COHR_DCF_and_Analysis/dcf.py`. Exit code: **0**. No DCF assumptions were changed. Source: [saved DCF script](COHR_DCF_and_Analysis/dcf.py).

The actual sensitivity output was:

```text
Sensitivity grid (USD per diluted share)
WACC / terminal g          2%          3%          4%
9%                      59.60       69.78       84.03
10%                     49.84       57.20       67.01
11%                     42.28       47.80       54.90
```

The minimum is $42.28 at 11% WACC / 2% terminal growth; the maximum is $84.03 at 9% / 4%. The five forecast FCFF amounts are -$594.00M, $189.75M, $726.11M, $1,144.45815M and $1,178.7918945M. Base-case enterprise value is $12,445.90M; adding $1,987.018M cash/investments and subtracting $3,257.482M debt produces $11,175.44M equity value. Dividing by 195.387M diluted weighted-average shares produces $57.20. Terminal value supplies **86.5%** of enterprise value.

The COHR reverse-DCF block reports no solution within its +/-$500M annual FCFF-shift bounds. Its $24.12–$90.28 reachable-price interval is a different experiment, not the Week 3 sensitivity range above. The separate hypothetical $30 training scenario is not COHR and contributes nothing to this comparison.

## Peer result and source trace

The [saved business-policy and Lab 07 output record](Deal%20Evidence%20and%20Valuation%20Triangulation/COHR%20Business%20Model%20%26%20Peer%20Multiple%20Policy.md) contains the actual run and candidate reasoning.

| Company | September 15 price | Annual reported GAAP diluted EPS | Fiscal year-end | Annual release published | Treatment |
|---|---:|---:|---|---|---|
| COHR | $271.17 | $4.12 | June 30, 2026 | August 12, 2026 | Target; own P/E 65.817961x |
| FN | $374.91 | $13.05 | June 26, 2026 | August 17, 2026 | Qualified business peer; only usable multiple |
| LITE | $838.96 | -$92.96 | June 27, 2026 | August 11, 2026 | Business candidate, excluded from reported annual P/E |

Price locators: Investing.com historical tables, **September 15, 2026 row, Price column**, for [COHR](https://www.investing.com/equities/coherent-historical-data), [FN](https://www.investing.com/equities/fabrinet-historical-data), and [LITE](https://www.investing.com/equities/lumentum-holdings-inc-historical-data). Nasdaq historical pages returned unavailable data in the earlier investigation; these are secondary-provider prices, not claimed exchange verification.

Annual earnings locators:

- COHR: [SEC FY2026 10-K](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm), Item 8, Note 19, printed p. 85; [August 12 annual release](https://ir.coherent.com/news-releases/news-release-details/coherent-corp-reports-fourth-quarter-and-full-year-fiscal-2026), Table 1, FY2026 GAAP diluted EPS.
- FN: [SEC FY2026 10-K](https://www.sec.gov/Archives/edgar/data/1408710/000140871026000028/fn-20260626.htm), Item 8, Note 5, printed p. 74; [August 17 annual release](https://investor.fabrinet.com/node/13666), Fiscal Year 2026 Financial Highlights—GAAP Results.
- LITE: [SEC FY2026 10-K](https://www.sec.gov/Archives/edgar/data/1633978/000162828026057358/lite-20260627.htm), Item 8, Note 3, printed p. 83; [August 11 annual release](https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2026-Results/default.aspx), Full Fiscal Year 2026.

The calculation is `(374.91 / 13.05) * 4.12 = $118.36`, rounded at the end. Removing FN leaves no estimate; removing already-excluded LITE changes the reference by $0.00. Negative EPS supplies no meaningful positive-earnings P/E benchmark; zero EPS would make division undefined. No adjusted EPS, quarterly annualization, alternative model or substitute company is used.

## Skeptical colleague's review

**Weakest supported input: the 10% WACC.** The script explicitly labels it an unresolved placeholder. A 9%–11% grid tests arithmetic around that placeholder; it does not establish a defensible discount rate. Because terminal value accounts for 86.5% of enterprise value, this input is consequential. Evidence needed: a comparison-date risk-free yield, supported COHR beta and equity-risk premium, borrowing cost, tax shield and capital weights.

The largest operating assumption also needs support: annual FCFF recovers from the saved historical estimate of -$873.08M to +$1,178.79M in FY2031. The model assumes revenue reaches $13.811B, operating margin reaches 16.5%, capex falls to 8.5% of revenue and incremental working-capital investment falls to 1.5%. These are analyst forecasts, not reported outcomes. Orders, production ramp economics, sustainable margins and cash conversion would need to support that recovery.

| Check | Finding and implication |
|---|---|
| Company | Both final values refer to COHR. FN's price creates its multiple; $118.36 is an implied COHR price. No Asbury figures or independent training-case outputs belong in the comparison. |
| Date | Prices share September 15, 2026, and annual releases precede it. Fiscal year-ends differ slightly. The DCF uses June 30 cash/debt and annual weighted-average shares, not a fully updated September 15 bridge. It discounts FY2027–FY2031 at years 1–5 without a September-to-June stub adjustment. The saved quote timestamp is after hours, whereas the peer inputs use closing prices; the same $271.17 benchmark is retained, but the timestamps are not identical. |
| Valuation object | Compare equity value per COHR share, not the DCF's enterprise value with a share price. The DCF assumes all stated cash/investments are nonoperating, omits separate noncontrolling-interest/lease adjustments, and uses historical diluted weighted-average shares. Confirm consistent cash-flow scope and current dilution before treating its equity bridge as final. P/E already values equity; do not apply that cash/debt bridge a second time. |
| Earnings definition | The peer method uses annual GAAP diluted EPS consistently; the DCF uses future FCFF. Accounting earnings and cash flow are different measures. COHR's reported earnings include a business-sale gain; FN's earnings include a $56.7M unrealized investment gain (FN Note 7, pp. 75–76). Keep reported figures for this lab, but do not describe either as proven recurring earnings. |
| Peer economics | FN matches network/datacenter demand and manufacturing exposure, but contract manufacturing can have different margins, R&D, product ownership and risk from COHR. One multiple cannot demonstrate a robust peer range. |
| Policy consistency | The saved write-up says LITE fails the 50% revenue test and that the exclusion will be ignored, but later calls the percentage unresolved and excludes LITE. Those positions conflict. The supported record is **unresolved revenue percentage**, not a verified failure or waiver; negative EPS independently excludes it from this calculation. No policy revision is made here. |
| Unsupported interpretation | The description that LITE's loss was “orchestrated under GAAP” asserts intent without evidence. Its annual release identifies a noncash debt-extinguishment loss from convertible-note settlement. Record that transaction and its accounting effect without claiming deliberate earnings manipulation or substituting non-GAAP profit. |
| Monitoring metric | The DCF script compares observed OCF minus capex against a threshold taken from forecast FCFF. Those measures differ, including the financing/interest treatment. Its printed “defer” is not an independent validation of the valuation or a consistently defined cash-flow test. |

The exact comparison-date market-cap verification remains incomplete. [FinanceCharts FN history](https://www.financecharts.com/stocks/FN/summary/market-cap), September 15 row, reports approximately $13.435B, supporting the $5B screen; primary/date-matched share-count confirmation remains missing. LITE's annual datacenter/communications percentage requires an end-market reconciliation because Components/Systems categories include industrial products. These unresolved checks are retained, not treated as verified passes.

## One question that could change the decision

**Would you maintain your buy decision if COHR's capacity expansion did not produce the roughly $1.18 billion annual free cash flow forecast for FY2031? What evidence would make you change that decision?**

User response: **Yes.** I would change the buy decision if the AI-investment bubble crashed and demand for COHR's datacenter and communications products fell materially, or if the company built excess capacity and demand proved insufficient to absorb it. Evidence that would trigger reconsideration includes sustained order or revenue deterioration in Datacenter & Communications, rising excess inventory or unused manufacturing capacity, capacity spending that fails to translate into revenue and cash flow, and evidence that the roughly $1.18 billion FY2031 FCFF forecast is no longer achievable. This answer makes the decision rule demand- and execution-sensitive rather than dependent on one missed forecast number alone.

## Decision record

| Claim being assessed | Decision | Reason |
|---|---|---|
| The saved DCF produces $42.28–$84.03 and a $57.20 base case | **ACCEPT** | Reproduced by executing the unchanged saved script successfully; valid as conditional model output. |
| FN gives a $118.36 COHR reference under the stated reported-EPS inputs | **ACCEPT, conditional** | Arithmetic and the saved run agree; one usable multiple, with business and policy-evidence limitations. |
| These outputs establish that COHR is overpriced or settle the buy decision | **UNRESOLVED** | Unsourced WACC, unvalidated cash-flow recovery, bridge/timing limitations and one qualified peer prevent that conclusion. The user's decision rule is now explicit: reconsider if AI demand collapses or excess capacity develops. |
| Average the methods, invent a peer range, or include LITE's adjusted earnings | **REJECT** | Would conceal model differences or change the lab's reported annual earnings basis. |

Overall assessment: **UNRESOLVED as an investment decision; ACCEPT the calculations as conditional classroom results.** The current buy view is maintained conditionally. The decision would change if evidence showed an AI-demand collapse, materially weaker datacenter/communications demand, or excess capacity that prevents the forecast investment from producing sustainable cash flow. The original policy remains visible and unchanged in the linked policy record; this review flags inconsistencies rather than silently revising it.

## Final assessment: peer choice, DCF comparison, and decision

I chose Fabrinet because its FY2026 revenue is concentrated in the same demand channels as COHR: datacenter products and communications infrastructure together represent 81.2% of revenue. Its business also requires optical manufacturing capacity, inventory, production yields and capital investment. Those features make FN a useful operating comparison even though FN is primarily a contract manufacturer and COHR develops and sells its own photonics products. That difference is a material caveat because contract manufacturing can have different margins, R&D intensity, pricing power and asset ownership.

Lumentum remains a relevant business candidate because it sells optical components, transceivers and switches for cloud, AI and communications networks and also faces capacity and supply-chain investment risks. I excluded it from the P/E calculation because its latest annual reported GAAP diluted EPS was **-$92.96**. A negative earnings denominator cannot support a meaningful positive P/E; I did not replace it with adjusted EPS. Lumentum's annual datacenter/communications revenue percentage also remains unresolved.

The peer comparison adds a market-based check to the DCF. The DCF asks what COHR's forecast future cash flows are worth after reinvestment, debt, cash and discounting. The peer method asks what investors paid for a comparable company's latest reported earnings. The peer result can therefore reveal whether the DCF's implied value is far below or above a market earnings benchmark. It does not validate the DCF forecast.

The results differ because they value different things. The DCF's $57.20 base case and $42.28–$84.03 sensitivity range depend on a five-year FCFF recovery, a 10% placeholder WACC, a 3% terminal-growth assumption and a terminal value that supplies 86.5% of enterprise value. The FN comparison applies FN's 28.728736x equity P/E to COHR's $4.12 annual reported diluted EPS and produces a **$118.36 single-peer reference**. The two methods cannot be mechanically averaged: one is a discounted enterprise-to-equity cash-flow model and the other is an equity-to-equity earnings multiple, and only one peer has usable positive EPS.

### Decision

**Decision: initiate, conditionally.** I can defend the DCF sensitivity range of **$42.28–$84.03** as the model's tested range, with **$57.20** as its base case. I can report **$118.36** as a conditional single-peer reference, but I withhold a peer range because Lumentum has negative EPS and no second usable peer remains. I do not average $57.20 and $118.36, and I do not present either as a guaranteed fair value.

I would change the decision to watch-defer or do not initiate if evidence showed an AI-investment bubble crash, sustained deterioration in COHR's datacenter and communications demand, excess capacity or inventory, or capacity spending that failed to produce sustainable revenue, margins and cash flow. Evidence supporting continued initiation would be durable customer orders, successful capacity utilization, improving operating cash conversion after the investment period, and results that keep the FCFF recovery path credible.

### Answer to the skeptical question

Yes, I would maintain the buy decision even if COHR did not produce the roughly $1.18 billion annual FY2031 FCFF forecast by itself. I would change my decision if the miss reflected an AI bubble crash, much weaker demand, or excess capacity caused by building ahead of demand. The evidence that would change my view is sustained order or revenue deterioration, rising excess inventory, unused manufacturing capacity, and investment spending that fails to convert into durable cash flow. A temporary forecast miss with continuing demand and improving capacity utilization would require a revised valuation, but would not automatically end the buy thesis.

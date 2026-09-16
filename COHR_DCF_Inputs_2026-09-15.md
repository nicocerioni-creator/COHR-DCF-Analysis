# COHR DCF input research

Prepared September 15, 2026 for Coherent Corp. (NYSE: COHR). This memo maps the five training input groups to filing evidence and separates reported facts from calculations and assumptions. WACC, forecast cash flows, and terminal growth require further decisions before a company valuation can be run.

## Sources and date conventions

Primary source: [COHR FY2026 Form 10-K PDF](<NicolasCerioni/COHR-research/COHR_2026_10K_Report_Accessed_9.1.26.pdf>). Its cover identifies the year ended June 30, 2026 (PDF p. 1). [SEC filing](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm). All page locators below refer to the 176-page local PDF, not the filing's smaller printed page numbers. The saved PDF records access on September 1, 2026 at 5:24 p.m.; the figures were rechecked on September 15, 2026.

Financial statement amounts are presented in USD thousands and converted here to USD millions. Share counts from the EPS reconciliation are converted from thousands to millions. Training inputs are from the FIN439 DCF Framework (Lab 5).

The five requested phrases do not occur verbatim in the extracted PDF. Their underlying financial items were located in the statements and notes. The expanded phrase “weighted average cost of capital” appears in the goodwill audit discussion, but does not supply a numeric company-wide WACC.

## Five input groups

| Input | Training value | SEC sourced value or status | Unit | As-of date or period | Locator and basis |
|---|---|---|---|---|---|
| Starting FCFF | 100 | **−873.08407**, calculated provisionally as 79.514 + 190.267 × (1 − 21%) − 1,102.909. Underlying amounts are reported; the selection of 21% as the interest tax-shield rate is an assumption. | USD millions | FY ended 2026-06-30 | Cash flow statement, PDF p. 102: operating cash flow and PP&E capex; earnings statement p. 98: interest expense; Note 18 p. 145: 21% U.S. statutory tax rate. See reconciliation below. |
| Growth Years 1–5 | 8% / 6% / 5% / 4% / 3% | **Unresolved forecast.** No five-year FCFF growth schedule is disclosed. MD&A provides operating evidence, not five SEC-sourced forecast rates. | Annual FCFF growth percentages, or explicit FCFF amounts in USD millions | Prospective FY2027–FY2031; history through 2026-06-30 | Item 7, PDF pp. 78, 81, 83–84; three-year cash flow history p. 102. |
| WACC | 10% | **Unresolved.** The illustration below is conditional on unsourced equity-return assumptions and estimation choices. | Annual discount rate, % | Valuation date 2026-09-15; financial inputs through 2026-06-30 | Note 8 pp. 122–124; earnings statement p. 98; tax note p. 145. These do not establish a complete CAPM-based WACC. |
| Terminal Growth | 3% | **Unresolved assumption.** No SEC-sourced perpetual economy growth rate is established by this filing. Select a sustainable nominal long-run economy rate consistent with USD cash flows and WACC. | Annual perpetual nominal FCFF growth, % | Beyond FY2031 under a five-year forecast | No numeric locator for the requested input; long-run assumption must be supported separately. Training 3% is a benchmark only. |
| Cash / Debt / Shares | 50 / 300 / 50 | Cash and equivalents: **1,162.018**; debt carrying value: **3,222.224** (gross principal **3,257.482**); diluted weighted-average shares: **195.387**. | Cash and debt: USD millions; shares: millions | Cash/debt at 2026-06-30; shares are FY2026 weighted average | Balance sheet p. 96; Note 8 debt table p. 122; Note 19 EPS reconciliation pp. 151–152. Reported cash still requires a non-operating cash assessment. |

## Starting FCFF reconciliation and forecast evidence

Using the requested classroom formula and reported interest expense:

```text
Operating cash flow                           79.514
Interest expense                             190.267
Assumed tax rate for interest shield          21.0%
After-tax interest = 190.267 × 0.79           150.31093
Cash additions to property, plant & equipment 1,102.909
Starting FCFF = 79.514 + 150.31093 − 1,102.909
             = −873.08407 million USD
```

The 21% statutory rate is disclosed, but applying it to all company interest is a modeling choice, not a reported company tax shield. The FY2026 effective rate is 60.849 / 847.733 = approximately 7.18% (p. 98). MD&A attributes the low effective rate partly to tax-position releases, stock compensation benefits, and German tax-law changes (p. 76). A normalized marginal tax rate and the ability to use interest deductions remain to be confirmed.

For a cash-interest version, the cash flow supplement reports cash paid for interest of 189.256 million (p. 104). Substituting that amount gives **−873.88276 million** at the same assumed 21% rate. The table uses the expense-based classroom convention consistently; neither calculation is directly reported FCFF. Noncash debt-cost amortization is already added back in operating cash flow, so refine the interest adjustment before treating this as fully reconciled operating FCFF.

Capex here means the cash PP&E additions on p. 102. Separate intangible purchases of 7.174 million are excluded from this definition; including them would reduce the primary FCFF estimate to −880.25807 million. PP&E additions included in accounts payable of 371.779 million (p. 104) are noncash and are not added again to cash capex.

Historical cash flow evidence, USD millions (p. 102):

| Fiscal year ended June 30 | Operating cash flow | Cash PP&E capex | OCF minus capex, not FCFF |
|---|---:|---:|---:|
| 2024 | 545.731 | 346.816 | 198.915 |
| 2025 | 633.600 | 440.836 | 192.764 |
| 2026 | 79.514 | 1,102.909 | −1,023.395 |

MD&A reports Datacenter & Communications revenue growth of 40% in FY2026, following 43% in FY2025, driven by AI datacenter and communications demand (pp. 78, 81). Industrial revenue fell 10% in FY2026, primarily from divestitures (p. 78). Inventory investment constrained FY2026 operating cash flow (pp. 83–84). Revenue growth is not FCFF growth: working capital and reinvestment must be forecast separately.

Because starting FCFF is negative, multiplying it by positive growth rates would enlarge the loss. Follow the lab framework by building an explicit five-year recovery path with positive Year 5 FCFF. No recovery amounts have been invented or inserted into dcf.py.

## Cash, debt, and share reconciliation

- Cash: 1,162.018 million is reported cash and equivalents, not a proven excess-cash balance. Short-term investments add another 825.000 million, giving 1,987.018 million before assessing operating cash needs. Restricted cash of 35.156 million current and 571.222 million noncurrent is kept separate (p. 96).
- Debt: 7.916 current + 3,214.308 long-term = 3,222.224 million carrying value. Adding unamortized issuance costs and discount of 10.087 + 21.228 + 3.943 = 35.258 million reconciles to 3,257.482 million gross principal (p. 122). Gross principal is a provisional valuation proxy; neither amount is a measured market value of debt.
- Shares: 177.269 basic + 5.699 common-stock equivalents + 12.419 Series B if-converted shares = 195.387 million diluted weighted-average shares (p. 152), as requested. This period average differs from current diluted shares after issuance and preferred conversions.
- Other claims: the balance sheet reports noncontrolling interests of 334.705 million and operating lease liabilities of 316.210 million in total; Series B preferred stock is zero at year end (p. 96). Their valuation treatment must be consistent with the cash flows and discount rate before finalizing the enterprise-to-equity bridge.

## COHR stock price and reverse DCF target

**Target price: 271.17 USD per common share.**

- Market-data lookup: COHR, U.S. equity, using the web finance quote tool.
- Provider-reported latest trade timestamp: **2026-09-15 23:15:00 UTC**, equivalent to **September 15, 2026, 7:15 p.m. EDT** in Indianapolis/New York.
- Lookup retrieval time: approximately **2026-09-15 23:38 UTC / 7:38 p.m. EDT**.
- This is the latest quote returned at lookup, not a guarantee of an executable live price. The provider does not identify the trading session; the timestamp is after regular trading hours.
- [FinanceCharts COHR price history](https://www.financecharts.com/stocks/COHR/summary/price) independently lists **271.17 USD for September 15, 2026**. Its date-level close corroborates the price, not the quote tool's exact trade timestamp.

## Provisional WACC estimate

**Illustrative result: approximately 10.62%. The table remains unresolved because the company-specific equity inputs are not sourced.**

The training arithmetic is:

```text
Cost of equity = 4.5% + 1.3 × 5% = 11.0%
After-tax cost of debt = 6% × (1 − 25%) = 4.5%
WACC = 85% × 11% + 15% × 4.5% = 10.025% ≈ 10%
```

For a provisional COHR calculation, use the filing to estimate a historical debt cost and capital amounts, while explicitly retaining the training cost of equity as an assumption:

| Component | Value and calculation | Evidence or assumption |
|---|---|---|
| Cost of equity, Ke | 4.5% + 1.3 × 5% = **11.00%** | Training risk-free rate, beta, and equity risk premium only. These are not verified COHR inputs or current market estimates. |
| Historical pretax debt cost proxy, Kd | 190.267 / [(3,686.921 + 3,222.224) / 2] = **5.5077%** | FY2026 interest expense p. 98 divided by average FY2025/FY2026 debt carrying values p. 122. Includes accounting costs and hedge effects; not a current borrowing yield. |
| Assumed marginal tax rate, T | **21%** | U.S. statutory rate p. 145; assumed applicable tax shield, subject to jurisdiction and deductibility review. |
| After-tax debt cost | 5.5077% × (1 − 21%) = **4.3511%** | Calculated from the preceding proxy and assumption. |
| Common shares for equity capitalization | 212.615894 issued − 16.863102 treasury = **195.752792 million** | June 30, 2026 balance sheet p. 96; point-in-time common shares, not the EPS weighted average. |
| Equity market value proxy, E | 271.17 × 195.752792 = **53,082.284607 million USD** | September 15 quote × June 30 shares; mixed dates, pending an updated outstanding-share count. |
| Debt value proxy, D | **3,257.482 million USD** | Gross debt principal at June 30, 2026, Note 8 p. 122; assumed proxy for market debt value. |
| Weights | E / (E + D) = **94.2181%**; D / (E + D) = **5.7819%** | Calculated; two-component common equity/debt approximation. |

```text
WACC = [E / (E + D)] × Ke + [D / (E + D)] × Kd × (1 − T)
     = 0.9421814786 × 0.11
       + 0.0578185214 × 0.0550768583 × 0.79
     = 0.1061556880
     = 10.6156% ≈ 10.62%
```

This uses more filing information than the training 85/15 weights, but it is not a fully sourced COHR WACC. Complete it with a dated risk-free yield, a justified COHR beta, a sourced equity risk premium, current borrowing costs, a defensible tax shield, and updated market capital weights. Reconcile leases and noncontrolling interests with the valuation scope. Note 8 also discloses 5% senior notes and floating-rate facilities (pp. 122–124); these are financing terms, not by themselves a complete cost-of-capital estimate.

## Verification and next decisions

Statement pages 96, 98, 102, 104, 122, 145, and 152 were visually checked against extracted text. Debt, diluted shares, cash flow subtraction, and WACC arithmetic were recalculated.

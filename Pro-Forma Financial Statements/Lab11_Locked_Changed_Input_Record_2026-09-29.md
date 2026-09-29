# Lab 11 — locked changed-input record

Date: September 29, 2026. Company: Coherent Corp. (COHR).
Status: predictions recorded before full sensitivity runs. All four cases were selected by Nicolas. This commit locks the plan; do not overwrite its predictions after observing results. Record actual results separately.

## Baseline and controls

Source: `Pro-Forma Financial Statements/proforma.COHR.py`, repository baseline commit `64f0561` (model unchanged from `eea4467`). Inputs are in `ASSUMPTIONS["growth"]` and `ASSUMPTIONS["gross_margin"]`.

Change ONE input path at a time. Start each case from the original base assumptions, not the preceding case. Hold every other independent input and opening balance fixed. The Python model is unchanged by this record.

Years below are FY2027 / FY2028 / FY2029 / FY2030 / FY2031. Rates are percentages; shifts are absolute percentage points (pp), not relative percent changes. In Python, 5 pp = 0.05 and 2 pp = 0.02. Every revenue path compounds from FY2026 revenue of USD 7,118.181 million.

| Case | Input | Old/base path (%) | New path (%) | Shift in each affected year |
|---|---|---|---|---|
| G-L | Revenue growth (`growth`) | 35 / 25 / 18 / 12 / 8 | 30 / 20 / 13 / 7 / 3 | -5 pp, FY2027–FY2031 |
| G-H | Revenue growth (`growth`) | 35 / 25 / 18 / 12 / 8 | 40 / 30 / 23 / 17 / 13 | +5 pp, FY2027–FY2031 |
| M-L | Gross margin (`gross_margin`) | 39 / 40 / 41 / 41.5 / 42 | 37 / 38 / 39 / 39.5 / 40 | -2 pp, FY2027–FY2031 |
| M-H | Gross margin (`gross_margin`) | 39 / 40 / 41 / 41.5 / 42 | 41 / 42 / 43 / 43.5 / 44 | +2 pp, FY2027–FY2031 |

## Identical outputs for every run

- FY2031 operating profit / EBIT: `operating_income`, USD millions. Base: 3,182.105.
- FY2031 signed FCFE INCLUDING net borrowing: `fcfe`, USD millions. Base: 371.977. Preserve signed FCFE for all five years in the eventual supporting results.
- Value per common share: **Unavailable**, USD/share, for base and every case. Existing valuation discards negative FCFE and its terminal treatment is unresolved for this exercise. Do not use its positive-only value, discard negative years, or invent a terminal value. Negative FCFE by itself does not invalidate DCF.
- Report reconciliation and funding failures alongside results. Do not change borrowing limits, cash floors, or other inputs to make a case pass.

## Locked expected directions and rough sizes

All changes below are relative to base, in USD millions. EBIT estimates come from direct arithmetic; FCFE estimates are deliberately rough hypotheses, not results of full scenario runs or statistical confidence intervals. Financing can reverse the cash-flow effect of revenue growth.

| Case | Expected FY2031 EBIT change | Expected FY2031 signed FCFE change | Why |
|---|---|---|---|
| G-L | Down about 615 (to about 2,567) | Tentatively up by a few hundred; rough working range -100 to +400 | Lower sales reduce profit, but also reduce capex and inventory funding across five years. Less FY2030 revolver borrowing could mean less repayment in FY2031, offsetting lower operating cash generation. Direction is financing-dependent. |
| G-H | Up about 728 (to about 3,910) | Tentatively down by about 100–200; rough working range -250 to +50 | Higher sales raise profit but require more capex and inventory. Additional prior-year borrowing must be repaid in FY2031; higher EBIT need not mean higher final-year FCFE. Funding constraints may bind. |
| M-L | Down about 233 (to about 2,949) | Down roughly 200–450 | Lower gross profit reduces after-tax earnings; higher modeled COGS increases inventory needs. Additional revolver borrowing/repayment may amplify the decline and expose funding shortfalls. |
| M-H | Up about 233 (to about 3,415) | Up roughly 200–650 | Higher gross profit raises after-tax earnings and lowers modeled inventory needs. Stronger earlier cash generation may avoid some or all of the base FY2030 revolver draw and FY2031 repayment. |

FCFE direction for G-L/G-H is a testable financing hypothesis, not a promise. Preserve these predictions even if actual runs contradict them; explain the discrepancy in a separate results record.

### Arithmetic supporting the rough sizes

At base FY2031 gross margin and SG&A ratio, EBIT/revenue = 0.42 × (1 - 0.32) - 0.10 = 18.56%. Compounding the growth paths gives approximate FY2031 revenue of 13,829.1 / 17,145.0 / 21,067.3 for lower/base/higher growth. Thus EBIT changes by approximately -615.4 / +728.0 versus base.

For the margin cases, delta EBIT = 17,144.965 × (+/-0.02) × (1 - 0.32) = approximately +/-233.2. At the fixed 20% tax rate, the earnings contribution is approximately +/-186.5. The model's fixed inventory-days rule adds roughly +/-14.7 to FY2031 cash flow as COGS changes. Before financing effects, the combined difference is about +/-201.2.

A hand-calculation cash proxy (EBIT × 80% + depreciation + amortization - inventory investment - other working-capital investment - PP&E capex - intangible purchases) gives growth-case FY2031 differences of about -57.3 for G-L and +27.1 for G-H before interest and financing effects. This proxy is NOT FCFE and is not a reported output. Base FY2031 revolver repayment is 442.772; the revolver limit is 664. Changes in prior-year borrowing can therefore materially outweigh those small operating cash differences. Full annual financing logic has not been run for these cases.

## Business rationale and range labels

Revenue growth range: **judgment**, +/-5 pp each year. Customer investment in AI data centers and optical network upgrades creates demand for Coherent's transceivers and laser components. Coherent must win orders and have capacity to fulfill them. The lower case tests slower spending, adoption, or delivery; the higher case tests faster demand and execution. These percentages are sensitivity choices, not company guidance.

Gross-margin range: **judgment informed by history**, +/-2 pp each year. The saved FY2026 GAAP gross-margin anchor is approximately 37.50%. More efficient internal manufacturing—6-inch indium phosphide wafers, improved usable-chip yields, automation, and utilization—can lower unit costs. Lower margins test slower manufacturing improvements or pricing pressure; higher margins test stronger execution and product mix. These factors support the direction, not a measured company promise of a 2 pp change.

Relevant company sources:
- NVIDIA/Coherent agreement: customer purchase commitments plus separate funding for Coherent's R&D and manufacturing capacity. https://www.coherent.com/news/press-releases/nvidia-and-coherent-announce-strategic-partnership
- 6-inch InP manufacturing: more devices per wafer and lower die costs; die-cost savings are not the same as total transceiver cost savings. https://www.coherent.com/news/press-releases/worlds-first-6-inch-inp-scalable-wafer-fabs-paving-the-way-for-the-next-generation-of-lasers-for-ai-transceivers-and-6g-wireless-networks

Model limitations for interpretation: inventory is tied mechanically to COGS, so raising margin reduces inventory even when physical sales are unchanged. Faster growth does not automatically trigger additional capacity investment beyond the fixed capex/revenue rule. Margin cases do not add incremental capex or R&D. These are controlled one-input sensitivities, not complete business scenarios.

Next step: run these four cases only when requested, retaining signed annual cash flows and the identical outputs above. Store observed results and comparisons with these locked predictions separately.

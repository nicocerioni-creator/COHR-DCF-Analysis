"""COHR five-year pro forma and positive-only FCFE valuation, USD millions.

Run: python3 proforma.COHR.py
Adapted from Week 5/proforma.py; the original ABG files are unchanged.
Sources: local COHR-research/COHR_2026_10K_Report_Accessed_9.1.26.pdf:
  PDF 3: actual shares at August 10, 2026 (not diluted EPS shares).
  PDF 96: June 30, 2026 opening balance sheet; PDF 98: earnings.
  PDF 102: depreciation, amortization, capital spending; PDF 122: debt schedule.
Source directory: NicolasCerioni/COHR-research (relative to this file).

User-supplied assumptions are in ASSUMPTIONS. Additional modeling conventions:
* GAAP gross margin, SG&A and R&D include D&A and stock compensation.
  Do NOT subtract D&A twice. Depreciation and amortization are CFO add-backs.
* Amortization held at FY2026 280.334, capped at opening intangibles.
* No separate SBC add-back/stock issuance; compensation is treated as an
  economic cash-equivalent expense, so the share count remains constant.
* Forecast net income belongs to the parent; NCI income/distributions are zero.
* Other operating assets remain fixed; changes in net other working capital
  run through operating liabilities. This is an aggregate, not account detail.
* Restricted cash, short-term investments and other nonoperating accounts stay
  fixed. Restricted cash is NEVER available to fund deficits.
* Interest uses opening gross debt/revolver; funding transactions occur at
  year-end. Debt issuance costs are expensed in proportion to principal repaid.
* Contractual repayments follow the PDF122 table verbatim. No refinancing or
  new August2026 subsidiary facility is assumed. Review debt-note narrative
  against the maturity table before using this simplified model professionally.
* Revolver capacity 664 is the June2026 available amount; extension beyond its
  contractual life is not assumed (no new drawings in FY2031).
* No tax credit for losses, loss carryforwards or interest-income forecast.
* Terminal period is debt free; final operating margins continue, growth is 3%,
  and net reinvestment equals growth times closing modeled operating capital
  (net PP&E + net intangibles + inventory + net other operating WC).
  This explicitly changes reinvestment to a sustainable-growth convention.
* Valuation date June30,2026, using subsequently released FY2026 information;
  year-end discounting, not a contemporaneous historical trading recommendation.
* Per instruction, only positive FCFE is valued. Negative cash flows remain in
  statements and financing checks but are assigned zero valuation contribution.
  This is an assignment convention, not standard signed-cash-flow DCF.
* No separate addition of opening cash/investments or subtraction of existing
  debt from FCFE value. Nonoperating-asset value is outside this assignment value.
"""

from copy import deepcopy
from math import isfinite

YEARS = (2027, 2028, 2029, 2030, 2031)
ASSUMPTIONS = {
    "growth": (.35, .25, .18, .12, .08),
    "gross_margin": (.39, .40, .41, .415, .42),
    "sga_ratios": (.38, .36, .34, .33, .32),
    "rd_ratio": .10,
    "depreciation_ratio": 241.561 / 2999.343,
    "amortization": 280.334,  # Additional judgment: FY2026 run rate, asset-capped.
    "impairment": 0.0,
    "capex_ratios": (.14, .12, .10, .08, .07),
    "intangible_purchases": 7.174,
    "tax_rate": .20,
    "inventory_days": 2581.043 / 4449.141 * 365,
    "floor_plan_ratio": 0.0,  # None.
    "other_wc_ratio": -.05,
    "minimum_cash": 300.0,
    "revolver_limit": 664.0,
    "revolver_rate": .06,
    "scheduled_repayment": (7.916, 34.375, 93.629, 2135.625, 985.937),
    "discretionary_repayment": 0.0,
    "buyback": 0.0,
    "floor_plan_rate": 0.0,
    "debt_rate": .055,
    "cost_of_equity": .12,
    "wacc": .11,  # Retained as input; NOT used to discount FCFE.
    "terminal_growth": .03,
    "shares": 195.832246,
}

OPENING = {
    "revenue": 7118.181,
    "cash": 1162.018,
    "short_term_investments": 825.000,
    "restricted_cash": 35.156 + 571.222,
    "inventory": 2581.043,
    "ppe": 2999.343,
    "intangibles": 2884.474,
    "other_operating_assets": 1343.278 + 900.112,
    "other_assets": 78.892 + 4375.597 + 69.434 + 474.283,
    "gross_debt": 3257.482,
    "debt_costs": 10.087 + 21.228 + 3.943,
    "revolver": 0.0,
    "floor_plan": 0.0,
    "operating_liabilities": 1905.357 + 358.047 + 347.990,
    "other_liabilities": 61.371 + 173.248 + 540.610 + 254.839 + 197.966,
    "equity": 10903.495,
    "nci": 334.705,
}


def totals(r):
    r["assets"] = sum(r[k] for k in (
        "cash", "short_term_investments", "restricted_cash", "inventory",
        "ppe", "intangibles", "other_operating_assets", "other_assets"))
    r["debt"] = r["gross_debt"] - r["debt_costs"]
    r["liabilities"] = (r["debt"] + r["revolver"] + r["floor_plan"]
                        + r["operating_liabilities"] + r["other_liabilities"])
    r["total_equity"] = r["equity"] + r["nci"]
    r["liabilities_equity"] = r["liabilities"] + r["total_equity"]
    r["balance_gap"] = r["assets"] - r["liabilities_equity"]
    return r


def project(opening=OPENING, assumptions=ASSUMPTIONS):
    a = assumptions
    if len(YEARS) != len(a["growth"]) or a["cost_of_equity"] <= a["terminal_growth"]:
        raise ValueError("Invalid forecast length or terminal discount assumptions")
    p = totals(dict(opening))
    if abs(p["balance_gap"]) > 1e-7:
        raise ValueError("Opening balance sheet does not balance")
    out = []
    for i, year in enumerate(YEARS):
        r = dict(p)
        r["year"] = year
        r["revenue"] = p["revenue"] * (1 + a["growth"][i])
        r["gross_profit"] = r["revenue"] * a["gross_margin"][i]
        r["cost_of_sales"] = r["revenue"] - r["gross_profit"]
        r["sga"] = r["gross_profit"] * a["sga_ratios"][i]
        r["rd"] = r["revenue"] * a["rd_ratio"]
        r["depreciation"] = min(p["ppe"], p["ppe"] * a["depreciation_ratio"])
        r["amortization"] = min(p["intangibles"], a["amortization"])
        r["impairment"] = a["impairment"]
        r["operating_income"] = r["gross_profit"] - r["sga"] - r["rd"] - r["impairment"]
        r["repayment"] = a["scheduled_repayment"][i] + a["discretionary_repayment"]
        if r["repayment"] > p["gross_debt"] + 1e-7:
            raise ValueError(f"{year}: repayments exceed principal outstanding")
        r["gross_debt"] = max(0.0, p["gross_debt"] - r["repayment"])
        r["debt_cost_amortization"] = (
            p["debt_costs"] * r["repayment"] / p["gross_debt"] if p["gross_debt"] else 0.0)
        r["debt_costs"] = p["debt_costs"] - r["debt_cost_amortization"]
        r["cash_interest"] = p["gross_debt"] * a["debt_rate"] + p["revolver"] * a["revolver_rate"]
        r["interest"] = r["cash_interest"] + r["debt_cost_amortization"]
        r["pretax"] = r["operating_income"] - r["interest"]
        r["tax"] = max(0.0, r["pretax"]) * a["tax_rate"]
        r["net_income"] = r["pretax"] - r["tax"]
        r["inventory"] = r["cost_of_sales"] * a["inventory_days"] / 365
        r["change_inventory"] = r["inventory"] - p["inventory"]
        r["change_other_wc"] = a["other_wc_ratio"] * (r["revenue"] - p["revenue"])
        r["operating_liabilities"] = p["operating_liabilities"] - r["change_other_wc"]
        r["capex"] = r["revenue"] * a["capex_ratios"][i]
        r["intangible_purchases"] = a["intangible_purchases"]
        r["ppe"] = p["ppe"] + r["capex"] - r["depreciation"]
        r["intangibles"] = p["intangibles"] + r["intangible_purchases"] - r["amortization"]
        r["other_assets"] = p["other_assets"] - r["impairment"]
        r["buyback"] = a["buyback"]
        r["equity"] = p["equity"] + r["net_income"] - r["buyback"]
        r["operating_cash_flow"] = (
            r["net_income"] + r["depreciation"] + r["amortization"]
            + r["impairment"] + r["debt_cost_amortization"]
            - r["change_inventory"] - r["change_other_wc"])
        r["investing_cash_flow"] = -r["capex"] - r["intangible_purchases"]
        r["fcfe_before_revolver"] = r["operating_cash_flow"] + r["investing_cash_flow"] - r["repayment"]
        r["opening_cash"] = p["cash"]
        cash_before = p["cash"] + r["fcfe_before_revolver"] - r["buyback"]
        limit = a["revolver_limit"] if year <= 2030 else 0.0
        r["revolver_draw"] = min(max(0.0, a["minimum_cash"] - cash_before),
                                 max(0.0, limit - p["revolver"]))
        r["revolver_repayment"] = (p["revolver"] if year == 2031 else
            min(max(0.0, cash_before - a["minimum_cash"]), p["revolver"]))
        r["net_revolver"] = r["revolver_draw"] - r["revolver_repayment"]
        r["revolver"] = p["revolver"] + r["net_revolver"]
        r["fcfe"] = r["fcfe_before_revolver"] + r["net_revolver"]
        r["financing_cash_flow"] = -r["repayment"] - r["buyback"] + r["net_revolver"]
        r["change_cash"] = r["operating_cash_flow"] + r["investing_cash_flow"] + r["financing_cash_flow"]
        r["cash"] = p["cash"] + r["change_cash"]
        r["positive_fcfe"] = max(0.0, r["fcfe"])
        r["fcfe_pv"] = r["positive_fcfe"] / (1 + a["cost_of_equity"]) ** (i + 1)
        totals(r)
        r["cash_gap"] = r["cash"] - r["opening_cash"] - r["change_cash"]
        r["equity_gap"] = r["equity"] - p["equity"] - r["net_income"] + r["buyback"]
        r["ppe_gap"] = r["ppe"] - p["ppe"] - r["capex"] + r["depreciation"]
        r["intangibles_gap"] = r["intangibles"] - p["intangibles"] - r["intangible_purchases"] + r["amortization"]
        r["debt_gap"] = r["gross_debt"] - p["gross_debt"] + r["repayment"]
        r["fcfe_gap"] = r["fcfe"] - r["change_cash"] - r["buyback"]
        r["wc_gap"] = ((r["other_operating_assets"] - r["operating_liabilities"])
                       - (p["other_operating_assets"] - p["operating_liabilities"])
                       - r["change_other_wc"])
        r["cash_headroom"] = r["cash"] - a["minimum_cash"]
        r["revolver_headroom"] = limit - r["revolver"]
        # Failure-only controls make every check read zero when satisfied.
        r["cash_floor_shortfall"] = max(0.0, -r["cash_headroom"])
        r["revolver_limit_excess"] = max(0.0, -r["revolver_headroom"])
        r["negative_balance_check"] = sum(max(0.0, -r[k]) for k in (
            "cash", "gross_debt", "debt_costs", "ppe", "intangibles",
            "inventory", "operating_liabilities", "revolver"))
        out.append(r)
        p = r
    return out


ZERO_CHECKS = ("balance_gap", "cash_gap", "equity_gap", "ppe_gap",
               "intangibles_gap", "debt_gap", "fcfe_gap", "wc_gap")


def assert_balanced(results, tolerance=1e-7):
    for r in results:
        for key, value in r.items():
            if isinstance(value, (int, float)) and not isfinite(value):
                raise AssertionError(f"{r['year']} nonfinite {key}")
        for key in ZERO_CHECKS:
            if abs(r[key]) > tolerance:
                raise AssertionError(f"{r['year']} {key}: {r[key]}")
        for key in ("cash_headroom", "revolver_headroom", "revolver", "gross_debt",
                    "debt_costs", "ppe", "intangibles", "inventory", "operating_liabilities"):
            if r[key] < -tolerance:
                raise AssertionError(f"{r['year']} {key} below zero: {r[key]}")


def value_equity(results, a=ASSUMPTIONS):
    r = results[-1]
    ke, g = a["cost_of_equity"], a["terminal_growth"]
    if not 0 <= g < ke or a["shares"] <= 0:
        raise ValueError("Invalid terminal growth, cost of equity or shares")
    if r["gross_debt"] + r["revolver"] > 1e-7:
        raise ValueError("Debt-free terminal assumption requires all debt repaid")
    capital = r["ppe"] + r["intangibles"] + r["inventory"] + r["other_operating_assets"] - r["operating_liabilities"]
    terminal_nopat = r["operating_income"] * (1 + g) * (1 - a["tax_rate"])
    reinvestment = capital * g
    terminal_fcfe = terminal_nopat - reinvestment
    explicit_pv = sum(max(0, x["fcfe"]) / (1 + ke)**t for t, x in enumerate(results, 1))
    terminal_pv = max(0, terminal_fcfe) / (ke - g) / (1 + ke)**len(results)
    equity_value = explicit_pv + terminal_pv
    return {"explicit_pv": explicit_pv, "terminal_nopat": terminal_nopat,
            "terminal_reinvestment": reinvestment, "terminal_fcfe": terminal_fcfe,
            "terminal_pv": terminal_pv, "equity_value": equity_value,
            "per_share": equity_value / a["shares"],
            "omitted_negative_pv": sum(min(0, x["fcfe"]) / (1 + ke)**t for t, x in enumerate(results, 1))}


def print_table(title, fields, results):
    print(f"\n{title} | USD millions")
    print(f"{'':43}" + "".join(f"{r['year']:>15}" for r in results))
    for label, key, sign in fields:
        print(f"{label:43}" + "".join(f"{(0 if abs(r[key]) < 1e-8 else sign*r[key]):>15,.3f}" for r in results))


def self_test():
    """Exercise real failure paths and financing, not just baseline arithmetic."""
    base = project()
    assert_balanced(base)
    bad = deepcopy(base)
    bad[0]["balance_gap"] = 1
    try:
        assert_balanced(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError("Balance check failed to reject an imbalance")
    # Lower opening cash and increase investments equally: force revolver use.
    opening = dict(OPENING, cash=1100.0,
                   short_term_investments=OPENING["short_term_investments"] + OPENING["cash"] - 1100)
    financed = project(opening)
    assert_balanced(financed)
    assert any(r["revolver_draw"] > 0 for r in financed)
    assert any(r["revolver_repayment"] > 0 for r in financed)
    # Same scenario with no credit must expose, not plug, the cash shortfall.
    stressed = project(opening, dict(ASSUMPTIONS, revolver_limit=0.0))
    try:
        assert_balanced(stressed)
    except AssertionError:
        pass
    else:
        raise AssertionError("Funding shortfall was not detected")
    assert any(r["fcfe"] < 0 and r["positive_fcfe"] == 0 for r in base)
    print("Self-tests PASS: imbalance rejection, revolver draw/repayment, funding-shortfall detection, negative-FCFE exclusion.")


def main():
    results = project()
    print("COHR | FY2027-FY2031 | Opening June 30, 2026 | Floor plan: none")
    print("Year-end FCFE discounted at 12%; WACC 11% is not used for FCFE.")
    opening = totals(dict(OPENING))
    print(f"Opening: assets {opening['assets']:,.3f}; liabilities {opening['liabilities']:,.3f}; parent equity {opening['equity']:,.3f}; NCI {opening['nci']:,.3f}.")
    print_table("INCOME STATEMENT", [
        ("Revenue", "revenue", 1), ("Cost of sales (includes allocated D&A)", "cost_of_sales", -1),
        ("Gross profit", "gross_profit", 1), ("SG&A (includes allocated D&A)", "sga", -1),
        ("R&D (includes allocated D&A)", "rd", -1), ("Separate impairment", "impairment", -1),
        ("Operating income", "operating_income", 1), ("Interest including debt-cost amortization", "interest", -1),
        ("Pretax income", "pretax", 1), ("Tax", "tax", -1), ("Net income attributable to COHR", "net_income", 1)], results)
    print_table("BALANCE SHEET", [(label, key, 1) for label, key in [
        ("Unrestricted cash", "cash"), ("Short-term investments", "short_term_investments"),
        ("Restricted cash", "restricted_cash"), ("Inventory", "inventory"), ("Net PP&E", "ppe"),
        ("Net intangible assets", "intangibles"), ("Other operating assets", "other_operating_assets"),
        ("Other assets incl. goodwill", "other_assets"), ("TOTAL ASSETS", "assets"),
        ("Debt, net of issuance costs", "debt"), ("Revolver", "revolver"),
        ("Operating liabilities", "operating_liabilities"), ("Other liabilities", "other_liabilities"),
        ("TOTAL LIABILITIES", "liabilities"), ("COHR shareholders equity", "equity"),
        ("Noncontrolling interests", "nci"), ("TOTAL LIABILITIES AND EQUITY", "liabilities_equity")]], results)
    print_table("CASH FLOW STATEMENT AND FCFE", [
        ("Net income", "net_income", 1), ("Add depreciation", "depreciation", 1),
        ("Add intangible amortization", "amortization", 1), ("Add impairment", "impairment", 1),
        ("Add debt-cost amortization", "debt_cost_amortization", 1),
        ("Inventory investment", "change_inventory", -1), ("Other working-capital investment", "change_other_wc", -1),
        ("OPERATING CASH FLOW", "operating_cash_flow", 1), ("Cash PP&E spending", "capex", -1),
        ("Intangible purchases", "intangible_purchases", -1), ("INVESTING CASH FLOW", "investing_cash_flow", 1),
        ("Scheduled principal repayments", "repayment", -1), ("Revolver draw", "revolver_draw", 1),
        ("Revolver repayment", "revolver_repayment", -1), ("Buybacks", "buyback", -1),
        ("FINANCING CASH FLOW", "financing_cash_flow", 1), ("Net change in cash", "change_cash", 1),
        ("Opening cash", "opening_cash", 1), ("Closing cash", "cash", 1),
        ("FCFE before revolver financing", "fcfe_before_revolver", 1), ("FCFE including net borrowing", "fcfe", 1),
        ("Positive FCFE valued", "positive_fcfe", 1), ("Present value of positive FCFE", "fcfe_pv", 1)], results)
    print(f"{'FCFE status':43}" + "".join(f"{('negative FCFE' if r['fcfe'] < 0 else 'positive FCFE'):>15}" for r in results))
    print_table("CHECK BLOCK (zero required for reconciliation rows)", [(key, key, 1) for key in ZERO_CHECKS] + [
        ("Cash floor shortfall (must be zero)", "cash_floor_shortfall", 1),
        ("Revolver limit excess (must be zero)", "revolver_limit_excess", 1),
        ("Negative balance check (must be zero)", "negative_balance_check", 1)], results)
    print(f"Cash floor: ${ASSUMPTIONS['minimum_cash']:,.1f} million; actual year-end cash: "
          + " / ".join(f"${r['cash']:,.1f}" for r in results) + " million.")
    assert_balanced(results)
    print("PASS: all five years balance; cash, equity, PP&E, intangibles, debt, FCFE and working capital reconcile; minimum cash and credit limits respected.")
    draws = [r for r in results if r["revolver_draw"] > 1e-8]
    for r in draws:
        print(f"{r['year']} revolver draw: ${r['revolver_draw']:,.3f} million, primarily to fund scheduled principal repayment of ${r['repayment']:,.3f} million and expansion capex while preserving the $300 million cash floor.")
    v = value_equity(results)
    print("\nVALUATION | Positive-only FCFE assignment convention")
    for label, key in [("PV of positive forecast FCFE", "explicit_pv"),
                       ("Terminal FY2032 after-tax operating income", "terminal_nopat"),
                       ("Terminal FY2032 net reinvestment", "terminal_reinvestment"),
                       ("Terminal FY2032 FCFE (debt free)", "terminal_fcfe"),
                       ("PV of terminal value", "terminal_pv"), ("Equity value", "equity_value"),
                       ("PV of negative FCFE excluded by instruction", "omitted_negative_pv")]:
        print(f"{label}: ${v[key]:,.3f} million")
    print(f"Terminal share of value: {v['terminal_pv']/v['equity_value']:.2%}")
    print(f"Shares: {ASSUMPTIONS['shares']:.6f} million (actual common shares, not diluted).")
    print(f"VALUE PER SHARE: ${v['per_share']:,.2f}")
    print("Negative FCFE is funded in the statements but omitted from valuation by instruction; this is not standard signed-FCFE DCF.")
    print("Terminal net reinvestment = 3% of closing net PP&E + intangibles + inventory + net other operating WC.")
    print("No separate opening cash/investment adjustment; see module docstring for all implementation conventions.")


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        self_test()
    main()

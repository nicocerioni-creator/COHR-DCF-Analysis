from math import isfinite


YEARS = (2026, 2027, 2028, 2029, 2030)
ASSUMPTIONS = {
    "growth": 0.018,
    "gross_margin": 0.1705,
    "sga_ratios": (0.665, 0.655, 0.645, 0.645, 0.645),
    "depreciation_ratio": 82.4 / 3070.4,
    "impairment": 120.0,
    "capex": 250.0,
    "tax_rate": 0.255,
    "inventory_days": 2135.8 / (17999.0 - 3071.7) * 365,
    "floor_plan_ratio": 2027.0 / 2135.8,
    "other_wc_ratio": 0.008,
    "minimum_cash": 25.0,
    "revolver_limit": 850.0,
    "revolver_rate": 0.06,
    "repayment": 150.0,
    "buyback": 150.0,
    "floor_plan_rate": 0.0467,
    "debt_rate": 0.0544,
    "cost_of_equity": 0.10,
    "terminal_growth": 0.025,
    "shares": 17.951349,
}
OPENING = {
    "revenue": 17999.0,
    "inventory": 2135.8,
    "ppe": 3070.4,
    "other_assets": 6371.6,
    "cash": 40.4,
    "floor_plan": 2027.0,
    "debt": 3572.0,
    "other_liabilities": 2127.5,
    "equity": 3891.7,
    "revolver": 0.0,  # No opening revolver was specified.
}


def project(opening, assumptions):
    """Return annual statement rows without rounding intermediate values."""
    a = assumptions
    prior = dict(opening)
    results = []
    for year, sga_ratio in zip(YEARS, a["sga_ratios"], strict=True):
        r = {"year": year}
        r["revenue"] = prior["revenue"] * (1 + a["growth"])
        r["gross_profit"] = r["revenue"] * a["gross_margin"]
        r["cost_of_sales"] = r["revenue"] - r["gross_profit"]
        r["sga"] = r["gross_profit"] * sga_ratio
        r["depreciation"] = prior["ppe"] * a["depreciation_ratio"]
        r["impairment"] = a["impairment"]
        r["operating_income"] = (
            r["gross_profit"] - r["sga"] - r["depreciation"] - r["impairment"]
        )
        r["interest"] = (
            prior["floor_plan"] * a["floor_plan_rate"]
            + prior["debt"] * a["debt_rate"]
            + prior["revolver"] * a["revolver_rate"]
        )
        r["pretax"] = r["operating_income"] - r["interest"]
        r["tax"] = max(0.0, r["pretax"]) * a["tax_rate"]
        r["net_income"] = r["pretax"] - r["tax"]

        r["inventory"] = r["cost_of_sales"] * a["inventory_days"] / 365
        r["floor_plan"] = r["inventory"] * a["floor_plan_ratio"]
        r["capex"] = a["capex"]
        r["ppe"] = prior["ppe"] + r["capex"] - r["depreciation"]
        r["change_other_wc"] = a["other_wc_ratio"] * (
            r["revenue"] - prior["revenue"]
        )
        r["other_assets"] = (
            prior["other_assets"] + r["change_other_wc"] - r["impairment"]
        )
        r["repayment"] = a["repayment"]
        r["debt"] = prior["debt"] - r["repayment"]
        r["other_liabilities"] = prior["other_liabilities"]
        r["buyback"] = a["buyback"]
        r["equity"] = prior["equity"] + r["net_income"] - r["buyback"]

        r["change_inventory"] = r["inventory"] - prior["inventory"]
        r["change_floor_plan"] = r["floor_plan"] - prior["floor_plan"]
        r["operating_cash_flow"] = (
            r["net_income"] + r["depreciation"] + r["impairment"]
            - r["change_inventory"] - r["change_other_wc"]
        )
        r["fcfe"] = (
            r["operating_cash_flow"] - r["capex"]
            + r["change_floor_plan"] - r["repayment"]
        )
        r["opening_cash"] = prior["cash"]
        cash_before_revolver = prior["cash"] + r["fcfe"] - r["buyback"]
        r["revolver_draw"] = 0.0
        r["revolver_repayment"] = 0.0
        if cash_before_revolver < a["minimum_cash"]:
            r["revolver_draw"] = min(
                a["minimum_cash"] - cash_before_revolver,
                max(0.0, a["revolver_limit"] - prior["revolver"]),
            )
        else:
            r["revolver_repayment"] = min(
                cash_before_revolver - a["minimum_cash"], prior["revolver"]
            )
        r["revolver"] = (
            prior["revolver"] + r["revolver_draw"] - r["revolver_repayment"]
        )
        r["cash"] = (
            cash_before_revolver + r["revolver_draw"] - r["revolver_repayment"]
        )
        r["financing_cash_flow"] = (
            r["change_floor_plan"] - r["repayment"] - r["buyback"]
            + r["revolver_draw"] - r["revolver_repayment"]
        )
        r["change_cash"] = r["cash"] - prior["cash"]
        r["assets"] = r["inventory"] + r["ppe"] + r["other_assets"] + r["cash"]
        r["liabilities"] = (
            r["floor_plan"] + r["debt"] + r["other_liabilities"] + r["revolver"]
        )
        r["liabilities_equity"] = r["liabilities"] + r["equity"]
        r["balance_gap"] = r["assets"] - r["liabilities_equity"]
        r["cash_headroom"] = r["cash"] - a["minimum_cash"]
        r["revolver_headroom"] = a["revolver_limit"] - r["revolver"]
        results.append(r)
        prior = r
    return results


def assert_balanced(results, tolerance=1e-7):
    """Raise with the year and gap for failed balance/cash/revolver checks."""
    for r in results:
        checks = (
            ("assets minus liabilities minus equity", r["balance_gap"], True),
            ("cash minus minimum", r["cash_headroom"], False),
            ("revolver limit minus balance", r["revolver_headroom"], False),
            ("revolver balance", r["revolver"], False),
        )
        for name, gap, must_equal_zero in checks:
            failed = abs(gap) > tolerance if must_equal_zero else gap < -tolerance
            if not isfinite(gap) or failed:
                raise AssertionError(
                    f'{r["year"]}: {name} check failed; gap = {gap:+.9f} USD millions'
                )


def print_table(title, rows, results):
    """Rows are (label, result key, display multiplier)."""
    print(f"\n{title} (USD millions)")
    print(f'{"":<39}' + "".join(f'{r["year"]:>14}' for r in results))
    for label, key, multiplier in rows:
        values = [r[key] * multiplier for r in results]
        print(f"{label:<39}" + "".join(
            f"{(0.0 if abs(value) < 0.05 else value):>14,.1f}" for value in values
        ))


def value_equity(results, assumptions):
    a = assumptions
    if a["cost_of_equity"] <= a["terminal_growth"]:
        raise ValueError("Cost of equity must exceed terminal growth")
    explicit_pv = sum(
        r["fcfe"] / (1 + a["cost_of_equity"]) ** t
        for t, r in enumerate(results, 1)
    )
    terminal_value = (
        (results[-1]["fcfe"] + results[-1]["repayment"])
        * (1 + a["terminal_growth"])
        / (a["cost_of_equity"] - a["terminal_growth"])
    )
    terminal_pv = terminal_value / (1 + a["cost_of_equity"]) ** 5
    equity_value = explicit_pv + terminal_pv
    return equity_value, terminal_pv / equity_value, equity_value / a["shares"]


def main():
    results = project(OPENING, ASSUMPTIONS)
    print("ABG projection | Year-end cash flows | Opening revolver assumed zero")
    print_table("INCOME STATEMENT", [
        ("Revenue", "revenue", 1), ("Cost of sales", "cost_of_sales", -1),
        ("Gross profit", "gross_profit", 1), ("SG&A", "sga", -1),
        ("Depreciation", "depreciation", -1), ("Impairment", "impairment", -1),
        ("Operating income", "operating_income", 1), ("Interest", "interest", -1),
        ("Pretax income", "pretax", 1), ("Tax", "tax", -1),
        ("Net income", "net_income", 1),
    ], results)
    print_table("BALANCE SHEET", [
        ("Cash", "cash", 1), ("Inventory", "inventory", 1),
        ("PP&E", "ppe", 1), ("Other assets", "other_assets", 1),
        ("Total assets", "assets", 1), ("Floor plan", "floor_plan", 1),
        ("Term debt", "debt", 1), ("Revolver", "revolver", 1),
        ("Other liabilities", "other_liabilities", 1),
        ("Total liabilities", "liabilities", 1), ("Equity", "equity", 1),
        ("Total liabilities and equity", "liabilities_equity", 1),
    ], results)
    print_table("CASH FLOW STATEMENT", [
        ("Net income", "net_income", 1), ("Add depreciation", "depreciation", 1),
        ("Add impairment", "impairment", 1),
        ("Inventory investment", "change_inventory", -1),
        ("Other working-capital investment", "change_other_wc", -1),
        ("Operating cash flow", "operating_cash_flow", 1),
        ("Investing cash flow: capex", "capex", -1),
        ("Change in floor plan", "change_floor_plan", 1),
        ("Term debt repayment", "repayment", -1),
        ("FCFE (before buybacks/revolver)", "fcfe", 1),
        ("Share buyback", "buyback", -1), ("Revolver draw", "revolver_draw", 1),
        ("Revolver repayment", "revolver_repayment", -1),
        ("Financing cash flow", "financing_cash_flow", 1),
        ("Net change in cash", "change_cash", 1),
        ("Opening cash", "opening_cash", 1), ("Closing cash", "cash", 1),
    ], results)
    print_table("ANNUAL CHECKS", [
        ("Assets - liabilities - equity", "balance_gap", 1),
        ("Cash above minimum", "cash_headroom", 1),
        ("Unused revolver capacity", "revolver_headroom", 1),
    ], results)
    assert_balanced(results)
    print("All annual balance, minimum-cash, and revolver checks passed.")
    equity_value, terminal_share, per_share = value_equity(results, ASSUMPTIONS)
    print(f"\nEquity value: ${equity_value:,.2f} million")
    print(f"Share of value after 2030: {terminal_share:.2%}")
    print(f"Value per share: ${per_share:,.2f}")


if __name__ == "__main__":
    main()
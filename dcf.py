# COHR classroom DCF: money and shares are in millions; rates are decimals.
from math import isfinite

# FY2026 historical estimate: OCF + interest expense * (1 - 21%) - PP&E capex.
# 10-K PDF pp. 98, 102, 145. The 21% tax-shield rate is an assumption.
# Retained for reference; FCFF_PATH overrides the starting-value growth method.
STARTING_FCFF = -873.08407

# Approved analyst forecast for FY2027-FY2031, not company guidance.
# FCFF = revenue * (operating margin * (1 - 21%) + D&A% - capex% - change-in-WC%).
# Revenue: 10000, 11500, 12650, 13409, 13811.27.
# Operating margin: 14%, 15%, 16%, 16.5%, 16.5%; D&A: 6%, 5.8%, 5.6%, 5.5%, 5.5%.
# Capex: 15%, 12%, 10%, 8.5%, 8.5%; additional WC: 8%, 4%, 2.5%, 1.5%, 1.5%.
# Evidence: FY2026 10-K PDF pp. 74-75, 83-84, 98, 102 and Aug. 12, 2026 outlook:
# https://ir.coherent.com/news-releases/news-release-details/coherent-corp-reports-fourth-quarter-and-full-year-fiscal-2026
FCFF_PATH = [-594.0, 189.75, 726.11, 1144.45815, 1178.7918945]

# PLACEHOLDER: training growth rates, unused while FCFF_PATH is populated.
YEARLY_GROWTH_RATES = [0.08, 0.06, 0.05, 0.04, 0.03]
WACC = 0.10  # UNRESOLVED PLACEHOLDER: training value, not a sourced COHR WACC.
WACC_IS_PLACEHOLDER = True
# Approved nominal long-run assumption; not company guidance.
# Economy reference: https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm
TERMINAL_GROWTH = 0.03
# June 30, 2026: all unrestricted cash + short-term investments treated as excess.
NON_OPERATING_CASH = 1987.018  # 1162.018 + 825.000; 10-K PDF pp. 96, 159.
DEBT = 3257.482  # Gross principal; 10-K Note 8, PDF p. 122.
DILUTED_SHARES = 195.387  # FY2026 weighted average; Note 19, PDF p. 152.
# Simplified classroom bridge: no separate lease or noncontrolling-interest adjustments.
SENSITIVITY_WACCS = [0.09, 0.10, 0.11]
SENSITIVITY_TERMINAL_GROWTH_RATES = [0.02, 0.03, 0.04]


def main():
    if TERMINAL_GROWTH >= WACC:
        raise SystemExit("Error: terminal growth must be less than WACC.")
    if WACC <= -1:
        raise SystemExit("Error: WACC must be greater than -1.")
    if DILUTED_SHARES <= 0:
        raise SystemExit("Error: diluted shares must be greater than zero.")

    if not isinstance(FCFF_PATH, (list, tuple)):
        raise SystemExit("Error: FCFF_PATH must be empty or contain five numeric amounts.")
    if FCFF_PATH:
        if len(FCFF_PATH) != 5 or any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) for value in FCFF_PATH
        ):
            raise SystemExit("Error: FCFF_PATH must contain exactly five finite numeric amounts.")
        yearly_fcff = list(FCFF_PATH)
    else:
        if len(YEARLY_GROWTH_RATES) != 5:
            raise SystemExit("Error: provide exactly five yearly growth rates.")
        if STARTING_FCFF <= 0:
            raise SystemExit("Error: use FCFF_PATH for a nonpositive starting FCFF.")
        yearly_fcff = []
        fcff = STARTING_FCFF
        for growth in YEARLY_GROWTH_RATES:
            fcff *= 1 + growth
            yearly_fcff.append(fcff)
    if yearly_fcff[-1] <= 0:
        raise SystemExit("Error: Year 5 FCFF must be positive for terminal valuation.")

    explicit_pv = sum(
        cash_flow / (1 + WACC) ** year
        for year, cash_flow in enumerate(yearly_fcff, start=1)
    )
    terminal_value = yearly_fcff[-1] * (1 + TERMINAL_GROWTH) / (
        WACC - TERMINAL_GROWTH
    )
    terminal_pv = terminal_value / (1 + WACC) ** len(yearly_fcff)
    enterprise_value = explicit_pv + terminal_pv
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    value_per_share = equity_value / DILUTED_SHARES
    if enterprise_value == 0:
        raise SystemExit("Error: enterprise value is zero; terminal value share is undefined.")
    terminal_share = terminal_pv / enterprise_value

    if WACC_IS_PLACEHOLDER:
        print(f"WACC: {WACC:.1%} (UNRESOLVED PLACEHOLDER: training value)")
    # Lab 5's agreed 12-line summary; round only the displayed results.
    for year, cash_flow in enumerate(yearly_fcff, start=1):
        print(f"{year}. Year {year} FCFF: ${cash_flow:,.2f}M")
    print(f"6. PV of five explicit cash flows: ${explicit_pv:,.2f}M")
    print(f"7. Terminal value at end of Year 5: ${terminal_value:,.2f}M")
    print(f"8. PV of terminal value: ${terminal_pv:,.2f}M")
    print(f"9. Enterprise value: ${enterprise_value:,.2f}M")
    print(f"10. Terminal share of enterprise value: {terminal_share:.1%}")
    print(f"11. Equity value: ${equity_value:,.2f}M")
    print(f"12. Value per diluted share: ${value_per_share:,.2f}")

    # Hold forecast FCFF and the capital bridge fixed across all scenarios.
    print("\nSensitivity grid (USD per diluted share)")
    print("WACC / terminal g" + "".join(
        f"{growth:>12.0%}" for growth in SENSITIVITY_TERMINAL_GROWTH_RATES
    ))
    for scenario_wacc in SENSITIVITY_WACCS:
        row = f"{scenario_wacc:<17.0%}"
        for scenario_growth in SENSITIVITY_TERMINAL_GROWTH_RATES:
            if scenario_wacc <= -1 or scenario_growth >= scenario_wacc:
                row += f"{'Invalid':>12}"
                continue
            scenario_explicit_pv = sum(
                cash_flow / (1 + scenario_wacc) ** year
                for year, cash_flow in enumerate(yearly_fcff, start=1)
            )
            scenario_terminal_value = (
                yearly_fcff[-1] * (1 + scenario_growth)
                / (scenario_wacc - scenario_growth)
            )
            scenario_terminal_pv = (
                scenario_terminal_value / (1 + scenario_wacc) ** len(yearly_fcff)
            )
            scenario_per_share = (
                scenario_explicit_pv + scenario_terminal_pv
                + NON_OPERATING_CASH - DEBT
            ) / DILUTED_SHARES
            row += f"{scenario_per_share:>12.2f}"
        print(row)


if __name__ == "__main__":
    main()

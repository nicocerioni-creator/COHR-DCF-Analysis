# COHR classroom DCF: money and shares are in millions; rates are decimals.
from math import isfinite, nextafter

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

# REVERSE DCF SETTINGS -- these do not change the base case or sensitivity grid.
# Enable/disable each section here rather than deleting its code.
RUN_CASH_FLOW_REVERSE = True
REVERSE_TARGET_PRICE = 271.17
REVERSE_TARGET_DATE = "2026-09-15 19:56:50 EDT (saved COHR quote, not live)"
# Bounds are USD millions ADDED to EACH annual FCFF, not percentage points.
# The lab's initial bounds may not reach the target: widen them deliberately
# (for example, an upper bound of 5000) to explore a larger recovery scenario.
FCFF_SHIFT_LOWER = -500.0
FCFF_SHIFT_UPPER = 500.0
REVERSE_PRICE_TOLERANCE = 1e-8  # USD per share, using unrounded values.

# SEPARATE GROWTH REVERSE -- original training case, not COHR assumptions.
# Set False to skip this block; preserve the settings and implementation.
RUN_GROWTH_REVERSE = True
GROWTH_REVERSE_STARTING_FCFF = 100.0
GROWTH_REVERSE_RATES = [0.08, 0.06, 0.05, 0.04, 0.03]
GROWTH_REVERSE_WACC = 0.10
GROWTH_REVERSE_TERMINAL_GROWTH = 0.03
GROWTH_REVERSE_CASH = 50.0
GROWTH_REVERSE_DEBT = 300.0
GROWTH_REVERSE_SHARES = 50.0
GROWTH_REVERSE_TARGET_PRICE = 30.0  # Hypothetical training target, not a quote.
# Units are percentage POINTS: -5 means subtract 0.05 from each growth rate.
GROWTH_SHIFT_LOWER_PP = -5.0
GROWTH_SHIFT_UPPER_PP = 10.0

# Conditional investment monitor; informational only and never an order.
# Values are trailing-four-quarter OCF minus capex in USD millions, newest last.
# FY2026 actual: 79.514 OCF - 1,102.909 PP&E capex = -1,023.395M.
ACTUAL_OCF_MINUS_CAPEX_HISTORY = [-1023.395]
REQUIRED_REPORTING_DATES = 2

# To value an adjusted FCFF path in the BASE CASE later, edit FCFF_PATH above.
# Example (commented out intentionally; enable only when you want a new base):
# FCFF_PATH = [amount + 100.0 for amount in FCFF_PATH]
# A reverse solution never overwrites FCFF_PATH automatically.


def finite_number(value):
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and isfinite(value)
    )


def reverse_price(path, wacc, growth, cash, debt, shares):
    """Value a separate scenario without changing any base-case inputs."""
    if not all(finite_number(x) for x in [wacc, growth, cash, debt, shares]):
        raise ValueError("valuation inputs must be finite numbers")
    if wacc <= -1 or growth <= -1 or growth >= wacc or shares <= 0:
        raise ValueError("require WACC > -100%, -100% < g < WACC, and shares > 0")
    if len(path) != 5 or not all(finite_number(x) for x in path) or path[-1] <= 0:
        raise ValueError("require five finite FCFF amounts and positive Year 5 FCFF")
    explicit = sum(x / (1 + wacc) ** t for t, x in enumerate(path, 1))
    terminal = path[-1] * (1 + growth) / (wacc - growth) / (1 + wacc) ** 5
    result = (explicit + terminal + cash - debt) / shares
    if not isfinite(result):
        raise ValueError("scenario valuation is not finite")
    return result


def bisect_reverse(price_function, target, lower, upper):
    """Return (shift or None, price at lower bound, price at upper bound).

    Both supported scenarios have increasing prices over their valid domain.
    A boundary is returned only if it actually matches the target to tolerance.
    """
    if not all(finite_number(x) for x in [target, lower, upper]):
        raise ValueError("target and bounds must be finite numbers")
    if lower >= upper:
        raise ValueError("lower bound must be less than upper bound")
    if not finite_number(REVERSE_PRICE_TOLERANCE) or REVERSE_PRICE_TOLERANCE <= 0:
        raise ValueError("price tolerance must be positive and finite")
    low_price, high_price = price_function(lower), price_function(upper)
    if high_price < low_price:
        raise ValueError("scenario prices must increase across the bracket")
    if abs(low_price - target) <= REVERSE_PRICE_TOLERANCE:
        return lower, low_price, high_price
    if abs(high_price - target) <= REVERSE_PRICE_TOLERANCE:
        return upper, low_price, high_price
    if target < low_price or target > high_price:
        return None, low_price, high_price
    for _ in range(200):
        midpoint = lower + (upper - lower) / 2
        value = price_function(midpoint)
        if abs(value - target) <= REVERSE_PRICE_TOLERANCE:
            return midpoint, low_price, high_price
        if midpoint == lower or midpoint == upper:
            break
        if value < target:
            lower = midpoint
        else:
            upper = midpoint
    raise ValueError("bisection did not converge to the requested price tolerance")


def print_cash_flow_reverse(path):
    """Solve one USD-million addition to every year of the approved FCFF path."""
    print("\nReverse DCF -- COHR uniform cash-flow addition")
    print(f"Target: ${REVERSE_TARGET_PRICE} per share; {REVERSE_TARGET_DATE}")
    print(
        f"Requested bounds: {FCFF_SHIFT_LOWER} to {FCFF_SHIFT_UPPER} USD millions per year"
    )
    print(f"Held fixed: original FCFF path (USD millions) = {path}")
    print(
        f"Held fixed: WACC = {WACC:.2%}"
        + (" (UNRESOLVED PLACEHOLDER)" if WACC_IS_PLACEHOLDER else "")
        + f"; terminal growth = {TERMINAL_GROWTH:.2%}"
    )
    print(
        f"Held fixed: cash = {NON_OPERATING_CASH}M; debt = {DEBT}M; "
        f"diluted shares = {DILUTED_SHARES}M; five year-end cash flows"
    )
    print(
        "Historical starting FCFF and training growth rates are inactive in this scenario."
    )
    try:
        lower, upper = FCFF_SHIFT_LOWER, FCFF_SHIFT_UPPER
        if not all(finite_number(x) for x in [lower, upper]) or lower >= upper:
            raise ValueError("require finite bounds with lower < upper")
        if path[-1] + upper <= 0:
            raise ValueError("no valid searched range: Year 5 FCFF must be positive")
        # Exclude all shifts leaving Year 5 nonpositive. nextafter moves just
        # above the excluded boundary without admitting a zero terminal FCFF.
        if path[-1] + lower <= 0:
            lower = nextafter(-path[-1], float("inf"))
            print(
                f"Valid lower bound adjusted to {lower:.12g}M; Year 5 must remain positive."
            )

        def price(shift):
            return reverse_price(
                [x + shift for x in path],
                WACC,
                TERMINAL_GROWTH,
                NON_OPERATING_CASH,
                DEBT,
                DILUTED_SHARES,
            )

        shift, low_price, high_price = bisect_reverse(
            price, REVERSE_TARGET_PRICE, lower, upper
        )
        print(
            f"Reachable prices in valid bracket: ${low_price:.6f} to ${high_price:.6f}"
        )
        if shift is None:
            print("No solution in this bracket. No bound is reported as a solution.")
            return
        print(f"Solved uniform FCFF addition: {shift:+.9f} USD millions per year")
        print(
            "Adjusted FCFF path (USD millions): "
            + ", ".join(f"{x + shift:.6f}" for x in path)
        )
        print(f"Matched price using unrounded shift: ${price(shift):.8f} per share")
    except (ValueError, OverflowError) as error:
        print(f"Reverse DCF invalid: {error}")


def growth_reverse_path(shift_pp):
    """Build five training FCFFs after adding a percentage-point shift."""
    value = GROWTH_REVERSE_STARTING_FCFF
    path = []
    for rate in GROWTH_REVERSE_RATES:
        adjusted_rate = rate + shift_pp / 100
        if adjusted_rate <= -1:
            raise ValueError("an annual growth rate would be -100% or below")
        value *= 1 + adjusted_rate
        path.append(value)
    return path


def print_growth_reverse():
    """Independent training example: do not modify COHR FCFF_PATH or its inputs."""
    print("\nReverse DCF -- separate training growth scenario (not COHR)")
    print(
        f"Target: ${GROWTH_REVERSE_TARGET_PRICE} per share (hypothetical training price)"
    )
    print(
        f"Requested bounds: {GROWTH_SHIFT_LOWER_PP} to {GROWTH_SHIFT_UPPER_PP} percentage points"
    )
    print(
        f"Held fixed: starting FCFF = {GROWTH_REVERSE_STARTING_FCFF}M; "
        f"original growth rates (decimals) = {GROWTH_REVERSE_RATES}"
    )
    print(
        f"Held fixed: WACC = {GROWTH_REVERSE_WACC:.2%}; "
        f"terminal growth = {GROWTH_REVERSE_TERMINAL_GROWTH:.2%}; "
        f"cash = {GROWTH_REVERSE_CASH}M; debt = {GROWTH_REVERSE_DEBT}M; "
        f"diluted shares = {GROWTH_REVERSE_SHARES}M; five year-end cash flows"
    )
    try:
        if (
            not finite_number(GROWTH_REVERSE_STARTING_FCFF)
            or GROWTH_REVERSE_STARTING_FCFF <= 0
        ):
            raise ValueError("growth scenario requires a positive finite starting FCFF")
        if (
            not isinstance(GROWTH_REVERSE_RATES, (list, tuple))
            or len(GROWTH_REVERSE_RATES) != 5
            or not all(finite_number(x) for x in GROWTH_REVERSE_RATES)
        ):
            raise ValueError("provide exactly five finite training growth rates")
        lower, upper = GROWTH_SHIFT_LOWER_PP, GROWTH_SHIFT_UPPER_PP
        if not all(finite_number(x) for x in [lower, upper]) or lower >= upper:
            raise ValueError("require finite bounds with lower < upper")
        # Reject the entire bracket if ANY permitted shift allows growth <= -100%.
        # The lower endpoint is the minimum rate for every year in this bracket.
        if any(rate + lower / 100 <= -1 for rate in GROWTH_REVERSE_RATES):
            raise ValueError(
                "bracket rejected: an annual growth rate reaches -100% or below"
            )

        def price(shift_pp):
            return reverse_price(
                growth_reverse_path(shift_pp),
                GROWTH_REVERSE_WACC,
                GROWTH_REVERSE_TERMINAL_GROWTH,
                GROWTH_REVERSE_CASH,
                GROWTH_REVERSE_DEBT,
                GROWTH_REVERSE_SHARES,
            )

        shift, low_price, high_price = bisect_reverse(
            price, GROWTH_REVERSE_TARGET_PRICE, lower, upper
        )
        print(f"Reachable prices in bracket: ${low_price:.6f} to ${high_price:.6f}")
        if shift is None:
            print("No solution in this bracket. No bound is reported as a solution.")
            return
        print(f"Solved uniform growth shift: {shift:+.9f} percentage points per year")
        print(
            "Adjusted annual growth rates: "
            + ", ".join(f"{100 * rate + shift:.6f}%" for rate in GROWTH_REVERSE_RATES)
        )
        print(f"Matched price using unrounded shift: ${price(shift):.8f} per share")
    except (ValueError, OverflowError) as error:
        print(f"Reverse DCF invalid: {error}")


def print_conditional_call(yearly_fcff):
    """Print the forecast-specific monitoring rule; do not initiate a trade."""
    print("\nConditional investment monitor (not financial advice)")
    if not isinstance(ACTUAL_OCF_MINUS_CAPEX_HISTORY, (list, tuple)):
        print(
            "Defer; this investment has not satisfied the conditions. This is not investment advice."
        )
        return
    forecast_threshold = yearly_fcff[0]
    history = ACTUAL_OCF_MINUS_CAPEX_HISTORY
    conditions_met = (
        len(history) >= REQUIRED_REPORTING_DATES
        and all(
            finite_number(value) and value >= forecast_threshold
            for value in history[-REQUIRED_REPORTING_DATES:]
        )
        and history[-1] > history[-2]
    )
    print(f"Forecast threshold: FY2027 OCF minus capex >= ${forecast_threshold:,.2f}M")
    print(f"Observed history (USD millions, newest last): {history}")
    print(f"Required reporting dates: {REQUIRED_REPORTING_DATES}")
    if conditions_met:
        print(
            "This investment seems promising; it may be a lucrative opportunity. This is not financial advice."
        )
    else:
        print(
            "Defer; this investment has not satisfied the conditions. This is not investment advice."
        )
    print(
        "Monitor: trailing-four-quarter operating cash flow minus capital expenditures."
    )


def main():
    if TERMINAL_GROWTH >= WACC:
        raise SystemExit("Error: terminal growth must be less than WACC.")
    if WACC <= -1:
        raise SystemExit("Error: WACC must be greater than -1.")
    if DILUTED_SHARES <= 0:
        raise SystemExit("Error: diluted shares must be greater than zero.")

    if not isinstance(FCFF_PATH, (list, tuple)):
        raise SystemExit(
            "Error: FCFF_PATH must be empty or contain five numeric amounts."
        )
    if FCFF_PATH:
        if len(FCFF_PATH) != 5 or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            for value in FCFF_PATH
        ):
            raise SystemExit(
                "Error: FCFF_PATH must contain exactly five finite numeric amounts."
            )
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
    terminal_value = yearly_fcff[-1] * (1 + TERMINAL_GROWTH) / (WACC - TERMINAL_GROWTH)
    terminal_pv = terminal_value / (1 + WACC) ** len(yearly_fcff)
    enterprise_value = explicit_pv + terminal_pv
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    value_per_share = equity_value / DILUTED_SHARES
    if enterprise_value == 0:
        raise SystemExit(
            "Error: enterprise value is zero; terminal value share is undefined."
        )
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
    print(
        "WACC / terminal g"
        + "".join(f"{growth:>12.0%}" for growth in SENSITIVITY_TERMINAL_GROWTH_RATES)
    )
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
                yearly_fcff[-1]
                * (1 + scenario_growth)
                / (scenario_wacc - scenario_growth)
            )
            scenario_terminal_pv = scenario_terminal_value / (1 + scenario_wacc) ** len(
                yearly_fcff
            )
            scenario_per_share = (
                scenario_explicit_pv + scenario_terminal_pv + NON_OPERATING_CASH - DEBT
            ) / DILUTED_SHARES
            row += f"{scenario_per_share:>12.2f}"
        print(row)

    # Optional scenarios leave the twelve lines and grid above unchanged.
    if RUN_CASH_FLOW_REVERSE:
        print_cash_flow_reverse(yearly_fcff)
    if RUN_GROWTH_REVERSE:
        print_growth_reverse()
    print_conditional_call(yearly_fcff)


if __name__ == "__main__":
    main()

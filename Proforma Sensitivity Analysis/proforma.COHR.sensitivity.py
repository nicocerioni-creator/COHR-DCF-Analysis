"""COHR Lab 11: standalone linked pro forma with one-at-a-time sensitivity.

Run: python3 proforma.COHR.sensitivity.py
Writes a Markdown report and full JSON audit beside this script by default.
Optional: --output-dir PATH

Basis: unchanged Lab 10 proforma.COHR.py at commit ba18386.
Locked ranges: Lab11_Locked_Changed_Input_Record_2026-09-29.md.
Source SHA256: e5c4345d841a1138350dec0b7fe3d02815313f93833cc6cac1d94db1eb0832ec
All historical inputs and accounting equations are inherited from Lab 10.
Source: FY2026 local COHR 10-K, PDF pages 3, 96, 98, 102 and 122.
Units: USD millions unless a ratio, percent, year or share unit is specified.
GAAP gross margin/SG&A already include D&A; no second expense deduction.
D&A added back to CFO; no separate SBC addback; NCI income is zero.
Interest on opening debt; contractual principal repayments at year-end.
Other WC changes through operating liabilities; restricted cash unavailable.
Short-term investments/restricted cash and other specified accounts stay fixed.
No refinancing; revolver closed in FY2031. Cash floor and limits unchanged.

Signed FCFE retained. Lab 10 positive-only valuation is NOT used: valuation
is unavailable under current instructions; no terminal value is computed.
This file preserves the linked operating/financing model, not its superseded
positive-only valuation. Invalid cases remain visible as diagnostics only.
"""
from copy import deepcopy
from math import isfinite
from types import MappingProxyType

YEARS = (2027, 2028, 2029, 2030, 2031)
BASE_ASSUMPTIONS = MappingProxyType({
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
})

BASE_OPENING = MappingProxyType({
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
})


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


def project(opening, assumptions):
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



# Exact locked paths; no newly selected ranges. Ratios are stored as decimals.
SCENARIOS = MappingProxyType({
    'growth': MappingProxyType({
        'lower': (.30, .20, .13, .07, .03),
        'base': BASE_ASSUMPTIONS['growth'],
        'higher': (.40, .30, .23, .17, .13),
    }),
    'gross_margin': MappingProxyType({
        'lower': (.37, .38, .39, .395, .40),
        'base': BASE_ASSUMPTIONS['gross_margin'],
        'higher': (.41, .42, .43, .435, .44),
    }),
})
VALUATION_REASON = (
    'Unavailable: Lab 10 excludes negative FCFE and its terminal treatment is '
    'unresolved for this exercise. Signed annual FCFE is retained; no terminal '
    'value is computed. Negative FCFE alone does not invalidate a valuation.'
)
CHECK_KEYS = ZERO_CHECKS + (
    'cash_floor_shortfall', 'revolver_limit_excess', 'negative_balance_check')
TOLERANCE = 1e-7  # USD millions, same tolerance as Lab 10.


def check_results(rows):
    """Collect every violation rather than hiding later years after one failure."""
    issues = []
    if len(rows) != len(YEARS) or tuple(r['year'] for r in rows) != YEARS:
        issues.append('Missing or mismatched forecast years')
    for r in rows:
        for key, value in r.items():
            if isinstance(value, (int, float)) and not isfinite(value):
                issues.append(f"FY{r['year']} {key}: nonfinite")
        for key in CHECK_KEYS:
            if abs(r[key]) > TOLERANCE:
                issues.append(f"FY{r['year']} {key}: {r[key]:,.6f} USD millions")
        for key in ('cash_headroom', 'revolver_headroom', 'revolver', 'gross_debt',
                    'debt_costs', 'ppe', 'intangibles', 'inventory', 'operating_liabilities'):
            if r[key] < -TOLERANCE:
                issues.append(f"FY{r['year']} {key}: {r[key]:,.6f} USD millions (below zero)")
    return issues


def run_case(case_id, driver=None, level='base'):
    # Fresh, independent dictionaries for BOTH input sets on EVERY run.
    assumptions = deepcopy(dict(BASE_ASSUMPTIONS))
    opening = deepcopy(dict(BASE_OPENING))
    if driver is not None:
        assumptions[driver] = tuple(SCENARIOS[driver][level])
    expected_changed = {driver} if driver and level != 'base' else set()
    actual_changed = {k for k in assumptions if assumptions[k] != BASE_ASSUMPTIONS[k]}
    if actual_changed != expected_changed:
        raise AssertionError(f'{case_id}: inputs were not reset to base')
    snapshot = deepcopy(assumptions)
    opening_snapshot = deepcopy(opening)
    rows, issues = [], []
    try:
        rows = project(opening, assumptions)
        issues = check_results(rows)
    except (ValueError, ArithmeticError) as exc:
        issues.append(f'Model execution failed: {exc}')
    if assumptions != snapshot or opening != opening_snapshot:
        raise AssertionError(f'{case_id}: model mutated independent inputs')
    final = rows[-1] if len(rows) == len(YEARS) else None
    return {
        'case': case_id, 'driver': driver, 'level': level,
        'input_units': 'decimal ratios; report displays percent',
        'output_units': 'USD millions; value_per_share would be USD/share',
        'assumptions': assumptions, 'opening': opening,
        'changed_inputs': sorted(actual_changed),
        'valid': not issues, 'issues': issues, 'statements': rows,
        'final_ebit': final['operating_income'] if final else None,
        'final_fcfe_including_net_borrowing': final['fcfe'] if final else None,
        'value_per_share': None, 'valuation_reason': VALUATION_REASON,
    }


def analyze():
    first = run_case('initial_base')
    if not first['valid']:
        raise AssertionError('Initial base failed: ' + '; '.join(first['issues']))
    cases = [first]
    for driver in SCENARIOS:
        for level in ('lower', 'base', 'higher'):
            case = run_case(f'{driver}_{level}', driver, level)
            for metric in ('final_ebit', 'final_fcfe_including_net_borrowing'):
                case['delta_' + metric] = (
                    case[metric] - first[metric] if case[metric] is not None else None)
            cases.append(case)
    # Explicitly restore all base inputs and rerun the entire linked model LAST.
    restored = run_case('restored_base')
    matched = all(restored[k] == first[k] for k in
                  ('assumptions', 'opening', 'statements', 'valid', 'issues'))
    if not matched:
        raise AssertionError('Restored base does not exactly match first run')
    cases.append(restored)
    spans = {}
    for driver in SCENARIOS:
        valid = [c for c in cases if c['driver'] == driver and c['valid']]
        spans[driver] = {'included': [c['level'] for c in valid],
                         'excluded': [c['level'] for c in cases
                                      if c['driver'] == driver and not c['valid']]}
        for metric in ('final_ebit', 'final_fcfe_including_net_borrowing'):
            vals = [c[metric] for c in valid]
            spans[driver][metric] = max(vals) - min(vals) if len(vals) >= 2 else None
        spans[driver]['value_per_share'] = None
    return {'years': YEARS, 'cases': cases, 'spans': spans,
            'restored_base_exact_match': matched, 'valuation_reason': VALUATION_REASON}


def number(value, signed=False):
    if value is None:
        return 'Unavailable'
    if abs(value) < 0.0005:
        value = 0.0
    return format(value, '+,.3f' if signed else ',.3f')


def path_percent(values):
    return ' / '.join(f'{v * 100:g}%' for v in values)


def report(data):
    lines = [
        '# COHR Lab 11 — one-at-a-time sensitivity results', '',
        'Years: FY2027 / FY2028 / FY2029 / FY2030 / FY2031. '
        'All monetary outputs and signed changes are USD millions, except value/share (USD/share).', '',
        'Each run uses fresh base assumptions and opening balances. Only the named input path changes. '
        'Linked statements are recalculated. Base copies and original Lab 10 file are preserved.', '',
        '**Valuation: ' + VALUATION_REASON + '**', '',
        '## Actual inputs and FY2031 results', '',
        'INVALID outputs are diagnostic calculations only; excluded from spans, with no ranking.', '',
        '| Case | Changed-driver path (%) | FY2031 EBIT | Change from base | FY2031 FCFE including net borrowing | Change from base | Value/share | Status |',
        '|---|---|---:|---:|---:|---:|---|---|',
    ]
    for c in data['cases']:
        driver_path = path_percent(c['assumptions'][c['driver']]) if c['driver'] else 'All base inputs'
        lines.append(f"| {c['case']} | {driver_path} | {number(c['final_ebit'])} | "
                     f"{number(c.get('delta_final_ebit', 0), True)} | "
                     f"{number(c['final_fcfe_including_net_borrowing'])} | "
                     f"{number(c.get('delta_final_fcfe_including_net_borrowing', 0), True)} | "
                     f"Unavailable | {'VALID' if c['valid'] else 'INVALID — diagnostic only'} |")
    lines += ['', '## Output spans: maximum minus minimum across valid cases only', '',
              '| Driver | Valid levels used | Excluded levels | EBIT span (USD millions) | FCFE span (USD millions) | Value/share span |',
              '|---|---|---|---:|---:|---|']
    for driver, span in data['spans'].items():
        lines.append(f"| {driver} | {', '.join(span['included'])} | {', '.join(span['excluded']) or 'None'} | "
                     f"{number(span['final_ebit'])} | {number(span['final_fcfe_including_net_borrowing'])} | Unavailable |")
    lines += ['', '**Restored base exactly matches the initial base across every input and annual statement field: PASS.**', '',
              '## Accounting and funding checks', '',
              'Reconciliation and failure-only checks require zero within 1e-7 USD millions. '
              'Validity covers every forecast year, not just FY2031.', '',
              '| Case | Maximum absolute reconciliation gap | Maximum cash-floor shortfall | Maximum revolver-limit excess | Maximum negative-balance check | Status |',
              '|---|---:|---:|---:|---:|---|']
    for c in data['cases']:
        rows = c['statements']
        vals = [max((abs(r[k]) for r in rows for k in ZERO_CHECKS), default=None)]
        vals += [max((r[k] for r in rows), default=None) for k in CHECK_KEYS[-3:]]
        lines.append('| ' + c['case'] + ' | ' + ' | '.join(number(v) for v in vals)
                     + ' | ' + ('PASS' if c['valid'] else 'FAIL') + ' |')
    for c in data['cases']:
        if c['issues']:
            lines += ['', f"**{c['case']} — INVALID:**"] + ['- ' + i for i in c['issues']]
    lines += ['', '## Annual signed FCFE including net borrowing (USD millions)', '',
              '| Case | FY2027 | FY2028 | FY2029 | FY2030 | FY2031 |',
              '|---|---:|---:|---:|---:|---:|']
    for c in data['cases']:
        lines.append('| ' + c['case'] + ' | ' + ' | '.join(number(r['fcfe']) for r in c['statements']) + ' |')
    summary = '\n'.join(lines) + '\n'
    lines += ['', '## Trace details for every run', '',
              'All annual computed fields are retained below and at full precision in the companion JSON. '
              'Expense and spending fields are positive magnitudes unless the field itself represents signed cash flow; '
              'the model equations specify subtraction. No positive-only cash-flow fields or terminal values are reported.']
    for c in data['cases']:
        lines += ['', '### ' + c['case'], '',
                  'Revenue growth: ' + path_percent(c['assumptions']['growth']) + '.', '',
                  'Gross margin: ' + path_percent(c['assumptions']['gross_margin']) + '.', '',
                  'All other independent assumptions and opening balances: base (full values in JSON).', '',
                  '| Statement/check field (USD millions) | FY2027 | FY2028 | FY2029 | FY2030 | FY2031 |',
                  '|---|---:|---:|---:|---:|---:|']
        rows = c['statements']
        if rows:
            for key in rows[0]:
                if key != 'year':
                    lines.append('| ' + key + ' | ' + ' | '.join(number(r[key]) for r in rows) + ' |')
    return summary, '\n'.join(lines) + '\n'


def main():
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    data = analyze()
    summary, full_report = report(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = 'COHR_Lab11_Sensitivity_Results'
    (args.output_dir / (stem + '.md')).write_text(full_report, encoding='utf-8')
    (args.output_dir / (stem + '.json')).write_text(
        json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(summary)
    print('Full statement report and JSON audit saved to:', args.output_dir)
    print('Execution completed; INVALID cases are retained diagnostics, not successful forecasts.')


if __name__ == '__main__':
    main()

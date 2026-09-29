"""Run with: python3 test_cohr_sensitivity.py (standard library only)."""
import importlib.util
from pathlib import Path
import unittest
from copy import deepcopy

spec = importlib.util.spec_from_file_location(
    'cohr_sensitivity', Path(__file__).with_name('proforma.COHR.sensitivity.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SensitivityTests(unittest.TestCase):
    def test_base_regression_and_restore(self):
        data = m.analyze()
        self.assertTrue(data['restored_base_exact_match'])
        base = data['cases'][0]
        self.assertAlmostEqual(base['final_ebit'], 3182.105, places=3)
        self.assertAlmostEqual(base['final_fcfe_including_net_borrowing'], 371.977, places=3)
        self.assertEqual(base['statements'], data['cases'][-1]['statements'])
        self.assertTrue(any(r['fcfe'] < 0 for r in base['statements']))
        self.assertIsNone(base['value_per_share'])
        self.assertFalse(any('positive_fcfe' in r for r in base['statements']))

    def test_run_order_and_input_isolation(self):
        first = m.run_case('first')
        scenario = m.run_case('higher', 'growth', 'higher')
        self.assertEqual(scenario['changed_inputs'], ['growth'])
        scenario['assumptions']['scheduled_repayment'] = (0,) * 5
        scenario['opening']['cash'] = 0
        scenario['statements'][0]['cash'] = 0
        last = m.run_case('last')
        self.assertEqual(first['assumptions'], last['assumptions'])
        self.assertEqual(first['opening'], last['opening'])
        self.assertEqual(first['statements'], last['statements'])
        with self.assertRaises(TypeError):
            m.BASE_ASSUMPTIONS['tax_rate'] = 0
        for driver in reversed(tuple(m.SCENARIOS)):
            for level in ('higher', 'base', 'lower'):
                result = m.run_case('repeat', driver, level)
                expected = m.run_case('repeat', driver, level)
                self.assertEqual(result, expected)

    def test_invalid_runs_excluded_from_spans(self):
        data = m.analyze()
        cases = {c['case']: c for c in data['cases']}
        self.assertFalse(cases['growth_higher']['valid'])
        self.assertFalse(cases['gross_margin_lower']['valid'])
        self.assertEqual(data['spans']['growth']['included'], ['lower', 'base'])
        self.assertEqual(data['spans']['gross_margin']['included'], ['base', 'higher'])
        self.assertLess(cases['gross_margin_lower']['final_fcfe_including_net_borrowing'], 0)
        for driver, span in data['spans'].items():
            valid = [c for c in data['cases'] if c['driver'] == driver and c['valid']]
            for key in ('final_ebit', 'final_fcfe_including_net_borrowing'):
                self.assertEqual(span[key], max(c[key] for c in valid) - min(c[key] for c in valid))

    def test_accounting_and_nonfinite_failures_detected(self):
        rows = deepcopy(m.run_case('base')['statements'])
        rows[0]['balance_gap'] = 1
        rows[-1]['cash_gap'] = 2
        rows[1]['net_income'] = float('nan')
        issues = m.check_results(rows)
        self.assertTrue(any('2027 balance_gap' in i for i in issues))
        self.assertTrue(any('2031 cash_gap' in i for i in issues))
        self.assertTrue(any('nonfinite' in i for i in issues))

    def test_only_locked_driver_changes(self):
        for driver in m.SCENARIOS:
            for level in ('lower', 'base', 'higher'):
                case = m.run_case('case', driver, level)
                for key, value in m.BASE_ASSUMPTIONS.items():
                    if key != driver:
                        self.assertEqual(case['assumptions'][key], value)
                self.assertEqual(case['assumptions'][driver], m.SCENARIOS[driver][level])
                self.assertEqual(case['opening'], dict(m.BASE_OPENING))


if __name__ == '__main__':
    unittest.main(verbosity=2)

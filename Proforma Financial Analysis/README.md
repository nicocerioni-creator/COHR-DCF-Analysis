# COHR Lab 11 sensitivity analysis

Standalone extension of the unchanged Lab 10 model in `../Pro-Forma Financial Statements/proforma.COHR.py`.
Uses the ranges locked in [the changed-input record](../Pro-Forma%20Financial%20Statements/Lab11_Locked_Changed_Input_Record_2026-09-29.md); no new company data or ranges.

Run from this folder with Python 3 (standard library only):

```sh
python3 proforma.COHR.sensitivity.py
python3 test_cohr_sensitivity.py
```

The script writes `COHR_Lab11_Sensitivity_Results.md` and `.json` beside itself. Use `--output-dir PATH` to choose another destination. The report shows actual annual input paths, FY2031 EBIT and signed FCFE including net borrowing, signed differences from base, valid-only spans, annual cash flows, accounting/funding checks, and all statement fields for each run. JSON retains full numerical precision, every assumption and opening balance, violations, and the restoration result.

All eight runs use independent copies: initial base; growth lower/base/higher; gross margin lower/base/higher; restored base. The base input templates are read-only. The restored base must match the first run exactly across inputs and all annual statement fields.

Value/share is unavailable in every case because the original positive-only FCFE valuation and terminal assumptions are unresolved for this exercise. No terminal value is calculated and no negative cash flow is discarded. Invalid cases retain diagnostic values but are excluded from spans. Validity requires all five years to satisfy the inherited accounting and funding checks. The script completing successfully does not mean every scenario is valid.

Verification: five automated tests passed. Separately compared all eight runs against the original Lab 10 model: all shared annual accounting fields matched exactly, and validity agreed with the original checker. Original Lab 10 file and locked prediction record were not modified.

Observed results are recorded without investment recommendations, driver rankings, or a written student interpretation.

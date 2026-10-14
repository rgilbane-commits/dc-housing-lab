# DC Housing Lab v1.6 — QC Audit

**Disposition: PASS WITH LIMITATIONS — hosted smoke test required.**

- Source baseline: v1.5.1 map hotfix.
- Changes: one new calculation module (`forecast.py`), one new app tab, reset button, opt-out map fallback, release documentation and forecast tests.
- Prior core `model.py`, `cash_flow.py`, `capital_stack.py`, `neighborhood_map.py`, `student_report.py` unchanged from baseline.
- Python compilation: PASS.
- Automated tests: **113 passed** (`python -m pytest -q`).
- Forecast unit tests: first-year rent/NOI reconciliation, ten-year count, annual cash waterfall identity, debt amortization including zero rates, Year 11 terminal capitalization, growth and inflation sensitivity, net sale reconciliation, input validation, zero-equity return handling.
- Formats: financial table uses shared USD formatter, metric percentage precision and × for multiples, CSV retains unformatted numeric data.
- Streamlit hosted startup and browser interaction: **NOT VERIFIED**. Streamlit is not installed in this local test runtime, and no hosted end-to-end test was executed. Map tiles are sourced online, so the off switch and dropdown fallback avoid dependence on rendering.

### Residual risks / caveats
1. Streamlit widgets and app rendering require a live hosted smoke test; unit tests cannot prove UI validity.
2. Student IRR is a simplified levered equity proxy and can be misleading when the capital stack is not fully funded; warning included.
3. Debt contracts can have balloons and different maturities; calculations assume originally specified amortizing schedules until sale, which can understate liquidity/refinancing risk.
4. Regulatory affordable rents do not necessarily rise at a constant rate; input is only illustrative.
5. Sale at the computed value is assumed, not guaranteed. Negative net sale to equity can imply liabilities; no limited-recourse treatment.
6. App does not use verified DC price, rent, income-limit, or parcel data.

### Mandatory browser verification
See README hosted acceptance checklist before labeling the release production-ready.

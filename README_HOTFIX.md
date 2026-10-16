# DC Housing Lab v2.7.3 Compatibility Hotfix

## Root cause
The v2.7.0 `development_returns.py` did not return `operating_deficit_total`, `operating_deficit_months`, or `refinance_equity_call`; v2.7.2 dashboard expects them. A dashboard-only update leaves incompatible versions deployed.

## Deploy
Replace BOTH files in the repository root: `development_returns.py` and `development_returns_dashboard.py`. Commit both together and reboot the Streamlit Cloud app. No `requirements.txt` changes are necessary.

This hotfix also provides an explicit version-mismatch message rather than an unhandled KeyError if older code is inadvertently deployed.

The financial engine is byte-identical to the v2.7.2 engine. The dashboard preserves the dependency-free IRR color table.

## QA
Run `python -m pytest -q tests` from the complete v2.7.2 application directory after installing dependencies. Live browser acceptance remains required.

# DC Housing Lab v2.7.2 hotfix

Fixes Streamlit Cloud `ImportError: background_gradient requires matplotlib` in the development returns 5x5 IRR sensitivity table.

**Minimal update**: replace `development_returns_dashboard.py` in the repository with the file from this release, then commit and redeploy. No changes to requirements.txt are needed.

**Full update**: unzip and upload the application files from this package.

**Verification**: Development Studio > Ten-year outlook > Development Returns; scroll to `Exit capitalization × construction cost sensitivity`. Ensure 25 cells render, colors follow fixed IRR thresholds, unavailable cells display N/A, and CSV export still works. The monthly calculations are unchanged.

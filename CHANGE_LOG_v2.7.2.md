# v2.7.2: Streamlit Cloud dependency hotfix

- Removed pandas `Styler.background_gradient()` from IRR matrix rendering, avoiding its undeclared matplotlib dependency on Python 3.14 Streamlit Cloud.
- Kept conditional heatmap coloring using `Styler.map()` and fixed annualized IRR thresholds (<0%, 0-5%, 5-10%, 10-15%, >=15%). Unavailable cells remain grey.
- No changes to `development_returns.py`, `model.py`, or other financial computational modules.
- Does not certify browser rendering; verify after deployment.

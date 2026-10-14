# DC Housing Lab v1.2.1 - Streamlit widget hotfix

## Incident
Clicking **Apply density bonus** in v1.2 raised `StreamlitWidgetAlreadyInstantiatedError` because `st.session_state.x_units` was assigned after its sidebar slider had been instantiated in the same script run. The same defect existed in the Public land contribution and Public grant buttons.

## Fix
Moved all three button state updates into Streamlit `on_click` callbacks. Streamlit runs callbacks before rebuilding widgets during a rerun. No underlying underwriting formulas changed.

## QA
- 22 unittest cases passed (20 existing plus two targeted callback regression tests).
- Python source compilation passed.
- Archive integrity must be verified as part of packaging.
- Hosted app interactive click-through remains unverified; test all three buttons after redeploying.

## Deploy
Upload **all files and folders inside this package** to the root of your existing GitHub repository, replacing matching files. Make sure `.streamlit/config.toml` and `tests/` directories remain intact. Commit to `main`. Streamlit Cloud should redeploy automatically. Refresh the app, then try the density, land, and grant buttons. You can verify the new version in the footer: `v1.2.1`.

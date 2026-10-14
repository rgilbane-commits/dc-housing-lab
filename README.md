# DC Housing Lab v1.2 — Sidwell Friends Classroom Edition

**For October 14, 2026.** This is an interactive Streamlit teaching app, not an actual DC development feasibility study. All neighborhood rent/cost/density inputs are **hypothetical**, not measured or verified zoning entitlements. AMI figure is an **editable classroom illustration, not the official HUD income limit**.

## Cloud deployment (Streamlit Community Cloud)

1. Extract the ZIP. Create a new GitHub repository (e.g., `dc-housing-lab`).
2. Upload the **contents** of the `DC_Housing_Lab_v1.2` folder so `app.py`, `model.py`, and `requirements.txt` are in the repository root. Keep `.streamlit/config.toml` if desired.
3. Log in at https://share.streamlit.io, select **Create app** / deploy from GitHub, select repository/branch, and set main-file path to **`app.py`**.
4. Open the generated public `*.streamlit.app` URL from a second device, test a slider and save/download proposal.
5. In class, students open the same public URL and use separate sessions. Each team **downloads its CSV**, sends it to the instructor, and the instructor uploads exports on the Classroom Challenge tab. There is **no shared live database**.

If upgrading an existing v1.0 GitHub deployment, **commit the v1.2 files to the same repo** (after downloading/saving a v1.0 backup); the app should redeploy automatically. To keep both versions live, use a separate v1.2 repository/deployment.

## Run locally

Python 3.10+ recommended.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Browser typically opens on `http://localhost:8501`. This is local, **not** a public URL.

## Tests

```bash
python -m unittest discover -s tests -v
python -m py_compile app.py model.py
```

## Release improvements

- Neighborhood assumptions: illustrative Friendship Heights, Columbia Heights, Congress Heights; explicit Load button prevents changing a selector silently overriding student edits.
- Household rent burden: income tiers 30%, 60%, 80%, 100% of **user-supplied hypothetical AMI**, with rent equal to 30% of gross income.
- Government choices: a 25% density bonus, a $10M land contribution, or a $10M grant. Separate repayable loan slider with annual amortizing payments.
- Classroom challenge, CSV collection, and instructor summary. No login, synced leaderboard, data collection service, or database.
- Explicit return-margin requirement and public-loan payments in simplified valuation. Not a real equity IRR or loan underwriting.

## Cautions

The app **does not** include land-use entitlements, tax credits, private debt, construction draws, financing fees, actual rent schedules, utility allowances, operating subsidies, actual site valuations, or current DC market comparables. The 'return margin' is a classroom capital-adequacy buffer, not an investor return or developer profit. Any negative residual NOI is flagged. Project feasibility shown is illustrative only.

For backup, retain the `DC_Housing_Lab_v1.0_Deploy.zip` independently.

## v1.2 classroom enhancements

- **Building visualization:** instructor view shows a responsive, color-coded unit-mix diagram. The display is capped at 100 tiles; tiles represent percentages, NOT individual apartment layouts or an actual building elevation. A separate text label reports exact unit counts.
- **Household stories:** four fictional household profiles, gross income, household size, housing budget, adjustable assumed utility allowance, and ability-to-pay comparisons to restricted and market rent. Income does not imply HUD eligibility.
- **Trade-off explanations:** model-calculated differences relative to the explicitly loaded neighborhood/scenario baseline; reports changes in affordable units, NOI, cost, grant and loan assumptions, and gap.
- **Expanded QC:** 20 Python unit tests and static interface-contract inspection. See `QA_AUDIT_REPORT.md` for results and limitations.

**Operating caution:** Runtime installation and live browser smoke testing were unavailable in the authoring environment due to network restrictions. Deployment requires a connected Streamlit host and a final smoke test. The public app URL does not exist until you deploy it.

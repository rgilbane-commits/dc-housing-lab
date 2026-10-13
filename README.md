# DC Housing Lab — Classroom Edition v1.0

An interactive Streamlit classroom app for affordable housing, urban planning, and the economics of development. Designed for an October 14, 2026 class at Sidwell Friends School, Washington, DC.

## Quick deploy (Streamlit Community Cloud)

1. Unzip this folder. Create a **new GitHub repository** (public for Streamlit Community Cloud free-tier deployment). Upload **all contents** including `app.py`, `model.py`, `requirements.txt`, and `.streamlit/config.toml` **at the repository root**. The `tests/` folder is optional for deployment but recommended to retain.
2. Sign in at https://share.streamlit.io/ with GitHub. Choose **Create app** → **Yup, I have an app**.
3. Select your repository, branch `main`, and **main file path `app.py`**. Choose Python 3.12 in Advanced settings if desired. Click **Deploy**.
4. Open the generated `https://...streamlit.app` URL on a laptop or phone. **Test it from an incognito window** before sharing with the class.

> Streamlit manages hosting; this ZIP by itself is not a publicly accessible site. Deployment needs your GitHub / Streamlit account. Exact interface labels may evolve.

Official deployment documentation: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local browser URL that Streamlit prints (usually http://localhost:8501). To run tests: `python -m unittest discover -s tests -v`.

## Teaching quickstart

1. On the **Today’s challenge** tab, introduce the three goals: ≥200 apartments; ≥60 income-restricted homes; funding gap ≤0.
2. In the sidebar, change income-restricted percentage from 30% to 100%. Talk about how value and funding gap shift.
3. Ask students to create their own proposal. Use the **Compare proposals** tab to save/export a CSV, then upload students' exports on the instructor's computer.
4. Discuss why a positive stabilized-value test is not evidence of an executable capital stack, and why 'income-restricted' does not necessarily mean affordable to every low-income household.

## What actually works

- Interactive density, rents, cost, subsidy, land, parking, and underwriting sliders.
- Recomputed unit counts, NOI, stabilized value, funding gap, cash subsidy requirement.
- Policy presets and discussion prompts.
- Session-local student proposals, exportable CSVs, and instructor CSV aggregation.
- Teaching guide and clearly labeled simplified assumptions.

## Limitations (disclose to students)

- **Not network-synchronized.** Each browser has its own independent session. The instructor manually imports CSV exports to compare proposals. No database, authentication, or persistent classroom leaderboard.
- **Not actual DC underwriting.** Default rent/cost/subsidy/cap assumptions are fictional, not verified market data. Model excludes loan sizing, debt costs, bond financing, project schedule, tax credits, tax abatements, reserves, developer fees, and tiered AMI rules.
- **No automatic live data feed.** For real-world data, add jurisdiction-specific rent restrictions, subsidy programs, and current underwriting evidence separately.
- **Value is not financeable proceeds.** Funding-gap proxy compares stabilized asset value and public support against net development cost; it is intentionally simplistic.
- **Land credits are economic support.** They reduce modeled net development cost and are distinguished from a cash subsidy.

## Model math

- Affordable homes = rounded(total homes × affordable percent).
- Gross annual rent = 12 × (market homes × market rent + restricted homes × restricted rent).
- Effective rent = gross rent × (1 − vacancy and collection loss).
- NOI = effective rent × (1 − operating expense ratio).
- Stabilized value = NOI / capitalization rate.
- Net cost = base development cost + incremental parking cost − land credit.
- Funding gap = net cost − value − public capital subsidy.

## Troubleshooting

- **Module not found:** Verify `requirements.txt` at repository root and inspect Streamlit app logs.
- **Blank app:** Check logs for Python errors; verify entrypoint `app.py`.
- **Sliders appear unchanged after selecting preset:** Click **Load scenario / reset sliders** in sidebar.
- **Students can't see instructor results:** Expected — use CSV export/import workflow.
- **App sleeps while idle:** Streamlit may put an unused free-tier app to sleep; open and test ahead of class.

## Project layout

```
app.py                    Streamlit UI
model.py                  Pure Python financial calculations
requirements.txt          Cloud dependencies
.streamlit/config.toml    Theme and server settings
README.md                 Setup and limitations
tests/test_model.py       Math checks
```

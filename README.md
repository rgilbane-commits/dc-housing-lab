# DC Housing Lab v1.6 — Deployment & Classroom Guide

## Deploy
1. Download and extract `DC_Housing_Lab_v1.6_Deploy.zip`.
2. Upload **the contents** to the root of the existing GitHub repository, including new `forecast.py`, updated `app.py`, tests, and existing modules.
3. Commit to the branch used by Streamlit Community Cloud, then open your deployed URL and check that the banner reads **v1.6**.
4. Run the hosted acceptance checklist below. Preserve the known-working v1.5.1 commit as a rollback point.

## What's new
- **Map fallback and reset:** uncheck **Display online interactive map** in Policy Lab if tiles fail. Use the sidebar neighborhood dropdown and **Load selected neighborhood and scenario** instead. **Reset project inputs** restores the selected neighborhood/preset and clears A/B comparisons.
- **Ten-year outlook:** New rightmost tab with separate annual market and restricted rent growth, operating expense inflation, vacancy, replacement reserves, exit capitalization rate, and selling cost percentage.
- The annual forecast includes rental income, operating expense, NOI, reserves, debt service, cash flow to equity, and remaining loan balances. Year-10 disposition capitalizes **Year 11 NOI**, deducts selling costs and the remaining public/private loan balances. Annual cash flows and sale proceeds are used to calculate an illustrative equity multiple and IRR.
- Downloadable ten-year CSV (numeric amounts retained).

## Hosted acceptance checklist
1. Open Policy Lab; uncheck Display online interactive map, then change the neighborhood using the sidebar dropdown and click Load. Confirm housing inputs update, regardless of map tile availability.
2. Click Reset project inputs and confirm preset values return.
3. Test Apply density bonus and Apply grant; no Streamlit widget-state error.
4. Open Ten-year outlook; change restricted rent growth, expense inflation and exit cap. Verify annual forecast and return metrics respond.
5. Set growth of restricted rents below expense inflation and verify the operating-margin warning.
6. Download the annual CSV and confirm currency values are numeric and years are 1–10.
7. Confirm capital stack and first-year operating waterfall continue to work.

## Methodology
Annual potential income is based on year-one rent and units. Market and restricted rents compound at separate rates; effective income deducts the selected forecast vacancy assumption. Operating expenses grow from the original stabilized expense dollars (not a fixed percentage of future revenue). Replacement reserve begins at units × annual reserve per unit and escalates at expense inflation. Debt payments are based on the private loan amount actually supported in the existing model, plus public debt; amortizing balances are rolled forward annually.

Net sale proceeds at the end of year 10 = Year 11 NOI / exit cap rate − sale transaction costs − unpaid public/private principal. Equity IRR includes all years' cash flow after replacement reserves and debt service plus net sale proceeds. Initial equity equals the total required equity as defined in the existing model, **whether or not committed equity is sufficient**. Excludes construction and lease-up, loan maturity refinancing/balloons and cash sweeps, income taxes, capital expenditures outside reserve contributions, rent-limit compliance, fees and reserve draws. The base model is intentionally classroom-oriented, not investment-grade underwriting. Negative sale proceeds signal a deficiency; the model does not allocate deficiencies among parties.

**Important:** Restricted rent growth is an illustrative what-if input and does not represent legal rent limits under any program. Values are not verified DC market or HUD program data. Forecast DSCR uses NOI before reserves; cash flow after reserves is reported separately.

## Source modules
`app.py`, `model.py`, `forecast.py`, `capital_stack.py`, `cash_flow.py`, `classroom.py`, `upgrade.py`, `neighborhood_map.py`, `student_report.py`, `visuals.py`, `display_format.py`, `requirements.txt`, `tests/`.

## Rollback
If hosted browser testing reveals a fault, use GitHub's commit history to revert to v1.5.1; do not delete existing repositories. The model.py and other original financial modules were not edited in v1.6.

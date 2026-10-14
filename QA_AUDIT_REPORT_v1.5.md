# DC Housing Lab v1.5 - QC Audit

**Release disposition: PASS WITH LIMITATIONS - deploy for hosted smoke testing, not yet browser-verified.**

## Scope

- Added interactive geographic neighborhood selection using Folium + streamlit-folium.
- Added presentation layout CSS with main-screen controls and F11 guidance.
- Added a one-page downloadable PDF project report using ReportLab.
- Preserved v1.4 financial modules: `model.py`, `cash_flow.py`, `capital_stack.py`, `upgrade.py`, `classroom.py`, `visuals.py`, `display_format.py`.

## Automated verification

- `python -m pytest -q`: **98 tests passed**, including 86 inherited tests and 12 tests for the v1.5 additions.
- `python -m compileall`: passed.
- Map checks: exact marker-center clicks, unrelated location, invalid click payload.
- PDF checks: all classroom presets, debt stress, 100% restricted housing, max density/cost and 1-page constraint.
- PDF rasterized to PNG and visually inspected: legible, no clipping or overflow.
- ZIP archive and source consistency: check on packaging.

## Open verification items

**VIS-001 (Medium / deployment validation):** Streamlit, streamlit-folium and Folium are not installed in this build environment, so live map click/re-render, responsive browser behavior and full-screen CSS have not been exercised in a running browser. Validate in hosted Streamlit after dependency installation.

**DATA-001 (Documented limitation):** Approximate neighborhood-center coordinates do not establish parcel location, zoning, or transit service area; all underlying underwriting scenarios remain illustrative.

**SEC-001 (Low):** Map tiles are loaded from an external map provider, so access requires internet connectivity and may be subject to third-party availability.

## Numeric/model integrity

- Underlying cash-flow, NOI, cap rate, debt capacity and margin calculations remain unmodified.
- PDF inputs use the `analyze(p)` result rather than recomputing the financing model.
- PDF currency amounts are formatted in dollars with grouping and preserved negative signs; percentages and DSCR are separately labeled.
- Classroom summary cash-on-cash is illustrative, using NOI less debt service divided by required equity; no reserves, taxes or capital expenditures modeled.

## Recommended acceptance decision

Do not mark live deployment fully approved until the five manual steps in README are completed. Preserve the previous v1.4 commit or tag as rollback.

# DC Housing Lab v2.3.1 QA / Audit Report

**Disposition: CONDITIONAL — pending live browser acceptance.**

## Results
- `python -m pytest -q tests`: **210 passed**.
- Python `compileall -q`: **passed**.
- Deployment ZIP integrity and SHA-256 manifest: checked in release assembly.
- Financial and GIS calculation modules compared byte-by-byte with v2.3.0: **11 identical**.
- New tests: immutable snapshot, A/B delta reconciliation, budget rejection, invalid snapshot rejection.

## Scope and controls
- Uses existing `assess_portfolio` feasibility screens; does not introduce new underwriting formulas.
- Allocation and screening outputs are illustrative. Delivered homes remain zero.
- Session snapshots are not durable storage; refreshing or starting a new session may clear them.
- Comparisons of equity shortfalls are not evidence of financeability.

## Unverified
- Live Streamlit rendering and browser interactions, including widgets and chart responsiveness.
- API-backed Census/GIS connections in the deployed environment.
- PDF export for a combined A/B report (not included in v2.3.1; CSV only).
- Visual accessibility and mobile-browser QA.

## Acceptance checklist
1. Open Investment Strategy; allocate a sum <= $100M.
2. Save A; modify geography, subsidy assumption, or financing control and save B.
3. Confirm the data table and three charts change and reconcile with the existing allocation/feasibility outputs.
4. Export CSV and verify A/B and delta figures.
5. Clear both snapshots; confirm the comparison disappears.
6. Verify the other four workspaces and existing reports continue to function.

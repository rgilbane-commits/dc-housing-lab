# DC Housing Lab v1.3.3 — QC Audit Report

**Disposition: PASS WITH LIMITATIONS (source/package); cloud UI smoke test pending.**

## Scope
Independent check of new sources-and-uses display, source reconciliation, existing model regressions, numeral formatting dependencies and deployable source package.

## Results
- Full `unittest` suite: **67 tests passed**, including 9 new capital-stack tests.
- `compileall`: passed.
- Funding bar: net development uses compared with grants + public debt + supportable private debt + equity commitments and additional equity needed.
- Sources-and-uses allocation sums to net cost (including funding surplus cases).
- Private debt uses **funded_private_debt** (capacity-constrained) rather than private debt requested.
- Underfunded projects display additional equity needed; overfunded projects disclose excess, not profitability.
- Dollars displayed via existing shared money formatter; CSV exports unformatted numeric amounts.
- No change to baseline financial modeling formulas or policy callbacks.

## Residual limitations
1. Streamlit is not installed in this execution environment; actual cloud deployment and interactive browser actions are not verified here. **Must smoke-test on Streamlit Community Cloud.**
2. This is a simplified static capital stack (not construction draws, return analysis, lender commitment, cash-flow waterfall or project IRR).
3. The model's public loan proceeds are assumed available and its grant/loan receipts can exceed project costs; the diagram shows excess proposed sources instead of interpreting them as earnings.
4. The displayed financing application order (grant, public loan, private debt, committed equity) is for explaining allocation only; it does not represent disbursement priority or lender legal seniority.
5. Inputs are illustrative and not verified DC project data.

## Mandatory live QA
Confirm v1.3.3 in footer, open Build a Project, adjust grant, public loan, private loan, cost, equity commitment, and land credit; verify bar responds and reconciles; check download CSV; test Policy Lab density bonus and Reality Check; if failure, revert GitHub deployment commit.

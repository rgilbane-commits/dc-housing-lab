# DC Housing Lab v1.3.1 — financing methodology correction

This release supersedes v1.3 and preserves the earlier density-bonus button hotfix and US number formatting.

## Deployment
1. Extract the ZIP and upload its **contents** to the root of your existing GitHub repository, replacing matching source files, including `app.py`, `model.py`, `upgrade.py`, `classroom.py`, and `tests/`.
2. Ensure `requirements.txt` remains in the repository root and Streamlit Cloud points to `app.py` on the deployed branch.
3. Commit changes; open the hosted app and confirm **v1.3.1** in the heading/footer.
4. Smoke test density bonus, public loan, grant, land contribution, Reality Check, sensitivity grid and proposals.
5. To roll back, revert the GitHub commit and redeploy v1.3.

Run tests locally with `python -m unittest discover -s tests -v` after installing `pip install -r requirements.txt`.

## Financial definitions
- **Unlevered stabilized value** = NOI / cap rate. NOI is BEFORE all debt service.
- **Economic margin gap** = development cost after modeled public land contribution × (1 + illustrative return-margin percentage) − cash grants − stabilized unlevered value. This is a *value-over-cost screen*, not investor IRR or capital stack gap.
- **Capital funding gap** = development cost after public land credit − grants − public loan proceeds − illustrative private debt commitments − illustrative equity commitments. Positive is an unfunded amount and negative is excess modeled funding sources. Assumed private capital is not verified/underwritten.
- **Public-only debt service coverage** = NOI / modeled annual public loan payment, when a public loan exists. It is NOT total DSCR, because private debt service is not modeled. Public-loan repayment schedules are simplified level annual payments.
- A public loan does not automatically fix the economic feasibility screen; a grant improves both the margin screen and funding gap.

The cost, rents, neighborhood assumptions, incomes, proposed financing, and cap rates are hypothetical and should not be used as factual DC market data or live underwriting. No database or external data access required. Student submissions are CSV-based.

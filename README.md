# DC Housing Lab v1.3.4 — Annual operating cash-flow waterfall

Drop-in upgrade from v1.3.3. Adds `cash_flow.py` and an annual operating waterfall beneath the capital stack in **Build a project**. Existing capital stack, scenarios, widgets, calculations and CSV exports retained.

## Deploy
Upload **all files and folders** from this ZIP to the root of the existing GitHub repository, including the new `cash_flow.py`. Commit to the connected branch and verify the hosted app shows **v1.3.4**. Revert the commit to roll back. Do not delete existing modules still imported by `app.py`.

## Validate
Run `python -m unittest discover -s tests -v`. In the hosted app: (1) verify the waterfall reconciles to NOI and debt service; (2) increase the public loan and observe higher payment and lower post-debt cash; (3) test zero debt and zero equity; (4) download waterfall CSV; (5) test density bonus and capital stack controls.

## Financial logic
Gross scheduled rent less modeled vacancy/collections = effective gross income. Less modeled operating expenses = NOI. NOI less annual public and private amortizing debt service = cash flow before reserves, capex and taxes. Cash-on-cash uses **full required equity**, even if not yet committed; an explicit warning flags missing equity. A funded/signed capital stack or a positive cash-on-cash value is not a distribution guarantee. All figures are hypothetical and annual (not a discounted cash-flow forecast).

This release contains only current code and consolidated current-release documentation. Historical fixes remain in Git history.

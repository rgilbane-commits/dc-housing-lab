# Independent-style QC Review — DC Housing Lab v1.3.4
Date: 2026-10-14
Disposition: **PASS WITH LIMITATIONS — live hosted-browser acceptance pending**

## Scope
Source review, existing automated regression suite, new annual cash-flow waterfall tests, Python compilation, artifact consistency, and ZIP archive integrity.

## Results
- **82/82 tests passed** (`python -m unittest discover -s tests -q`), including 15 new waterfall tests.
- Python source compiles without syntax errors.
- Existing density-bonus callbacks and capital-stack tests remain in regression suite.
- Annual arithmetic reconciles: scheduled rents minus vacancy loss minus operating expenses = NOI; NOI minus public/private debt service = cash flow to equity.
- Unlevered NOI is not reduced by loan payments when calculating asset value.
- Cash-on-cash uses total **required equity**, not merely committed equity; the UI flags unfunded equity.
- Negative operating cash flow is preserved, and no-equity/no-debt cases render N/A where appropriate.
- Raw CSV numbers remain numeric; dollar formatting is presentation-only.

## Open limitations / residual risk
1. **LIVE-001 (high, open):** Streamlit is not installed in the execution environment, so browser startup, widgets, CSS, and public hosting have not been verified. Test the hosted app before presenting.
2. **FIN-001 (medium, documented):** Stabilized annual illustration only; no lease-up, inflation, replacement reserves, capital expenditures, operating reserves, income taxes, construction financing or sale/refinancing. Cash flow shown is *before* these items and may overstate distributable cash.
3. **FIN-002 (medium, documented):** Public loan commitment is not capped by the DSCR lender sizing constraints; overleveraged outcomes are flagged but not automatically rejected.
4. **DATA-001 (low, documented):** Costs, rents, neighborhood assumptions and AMI examples are classroom hypotheticals, not verified District inputs.

## Required hosted smoke test
1. Open deployed v1.3.4 and expand **Build a project**.
2. Check visual and CSV: Gross rent - vacancy - opex = NOI; NOI - both debt payments = cash to equity.
3. Increase public loan: operating NOI remains constant and cash available to equity falls (private debt capacity may also change).
4. Set zero debt and verify no total DSCR, while cash flow equals NOI.
5. Confirm cash-on-cash ratio uses *required* equity and the app warns when committed equity is insufficient.
6. Test density bonus, grant, capital stack, Scenario A/B, and CSV download.

The automated pass is not a claim of completed external production verification.

# DC Housing Lab v1.3.1 — QC audit

**Disposition:** PASS WITH LIMITATIONS (code-level tests passed; live hosted UI not tested in this environment).

## Scope
Correct public debt versus grant treatment and separate economic margin test, capital funding sources/uses, and public-only debt service coverage without changing previously tested classroom capabilities.

## Findings and disposition
- **FIN-001 / CLOSED (code-level):** Prior version reduced property value by capitalizing NOI *after* public-loan payments. Corrected to unlevered NOI / capitalization rate independent of debt proceeds or service.
- **FIN-002 / CLOSED (code-level):** Public loans formerly worsened the return-margin gap and were not clearly represented as a financing source. New capital funding gap deducts public loan proceeds as a source; economic margin gap is unchanged.
- **FIN-003 / CLOSED (code-level):** Financing terms were conflated with valuation. Separate public-only DSCR, public annual loan payments and illustrative private capital commitments are displayed and labeled.
- **UX-001 / CLOSED (static review):** Eliminated obsolete guidance about capitalizing residual NOI after debt service; updated classroom labels.
- **DEP-001 / OPEN:** Actual hosted Streamlit browser test (widget clicks and display) remains unverified; Streamlit is not installed locally.
- **MOD-001 / ACCEPTED LIMITATION:** No loan sizing, interest/repayment on private financing, investor equity hurdle, tax-credit model, or true total DSCR. Private financing fields are *illustrative committed amounts* only.
- **MOD-002 / ACCEPTED LIMITATION:** Economic margin screen is a classroom proxy, not a standard investor return calculation; property valuation is simplified and independent of terms of financing.

## Test evidence
- 46 unittest cases: **46 PASSED** including 8 new explicit finance correction cases.
- Python syntax compilation: **PASS**.
- Audit includes checks for 1:1 effect of grants on both gaps, 1:1 effect of loans on funding gap but not value/margin, sensitivity invariance to loan amount, public-only DSCR and invalid private financing.
- Deployment package ZIP integrity verified during packaging.

## Required deployment smoke checks
1. Confirm version v1.3.1 visible.
2. Increase repayable public loan $0M → $10M: capital funding gap improves by $10M; economic margin gap and stabilized value remain unchanged; loan service rises and public-only DSCR appears.
3. Increase grant $0M → $10M: capital funding and economic margin gaps both improve by $10M.
4. Verify density bonus / public land / grant buttons do not throw Streamlit session-state widget errors.
5. Verify comparison CSV and sensitivity matrix load and values are currency formatted.

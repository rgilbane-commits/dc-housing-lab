# DC Housing Lab v1.2 — Independent-style QC Report

**Date:** 2026-10-13  
**Disposition:** PASS FOR SOURCE PACKAGE / CONDITIONAL FOR LIVE CLASSROOM USE  
**Scope:** Educational simulation, household examples, dynamic explanations, CSV workflow and deployable source.  
**Important:** This is an internal QC review, **not** an independently conducted third-party audit.

## Verified checks

| Check | Result | Evidence / notes |
| --- | --- | --- |
| Existing financial unit tests | PASS | 10 of 10 |
| New classroom and boundary tests | PASS | 10 of 10 |
| Neighborhood × preset matrix | PASS | 3 neighborhoods × 3 presets exercised |
| Loan vs grant differentiation | PASS | Loan incurs annual debt service; grant reduces modeled gap without repayment |
| Building mix | PASS | Counts correct across 0%, partial, 100% restricted and 1–2,000 units; display max 100 tiles |
| Household rental affordability | PASS | Fictional profile income budgets include adjustable tenant-paid utilities |
| Scenario explanations | PASS | Directionality and dollar/unit differences checked against underlying financial model |
| Source/required tabs | PASS | Static source inspection verifies major tabs and new functionality are present |
| Python syntax | PASS | `compileall` |
| Cloud/browser smoke test | NOT RUN | Streamlit not installed; network prevents fetching runtime dependency |
| Accessibility / mobile browser | NOT RUN | Requires hosted visual and keyboard testing |
| Multi-user live aggregation | OUT OF SCOPE | CSV collection, not real-time synced collaboration |
| Actual DC cost/rent/rent-limit verification | OUT OF SCOPE | All location and wage inputs explicitly fictional or illustrative |

## Key residual risks / findings

**QC-001 — Hosting verification pending (HIGH before classroom):** Package could not be tested running in a deployed Streamlit browser because `streamlit` is unavailable and outbound package installation failed. Instructor must complete deployment and run smoke checklist below. NOT CLOSED.

**QC-002 — Simplified underwriting (MEDIUM, accepted educational limitation):** Debt service is capitalized as a perpetuity-style reduction at the property's cap rate, although the public loan has a finite term. This is **not** equivalent to discounted cash flows, loan proceeds, capital stack sizing, IRR, or fully financed development feasibility. User interface describes this as a classroom proxy. ACCEPTED FOR CLASSROOM USE; NOT SUITABLE FOR INVESTMENT.

**QC-003 — Assumption provenance (MEDIUM, accepted educational limitation):** Neighborhood market rents/costs/densities and hypothetical household earnings are not verified current figures. Explicitly labeled hypothetical. ACCEPTED.

**QC-004 — Browser session persistence (LOW, accepted):** Saved proposals live only in a student's Streamlit session. Users must download CSVs before refresh/session expiration. ACCEPTED.

**QC-005 — Building massing (LOW, accepted):** Color tiles show mix, not actual building geometry/height. Explicit legend and textual counts avoid misrepresentation. ACCEPTED.

**QC-006 — Economic comparison baseline (LOW, accepted):** Trade-off messages compare custom edits to most recently *loaded* neighborhood preset, even if selector dropdown changes without pressing Load; sidebar explains selection behavior. ACCEPTED.

## Final deployment smoke checklist (in browser)

- [ ] App loads from public HTTPS URL on an instructor machine and a separate student device.
- [ ] Select different neighborhood + preset, click **Load**, confirm changed housing program assumptions.
- [ ] Move affordability slider 30% → 60%; verify mix diagram, restricted-home count, and trade-off messages update.
- [ ] Move apartments slider up; confirm home count and diagram update without errors.
- [ ] Change affordable rent and utility allowance; verify four household affordability responses change.
- [ ] Apply density, public land, and grant buttons; confirm numerical changes.
- [ ] Set public loan and check loan service / not-a-grant messaging.
- [ ] Save team proposal; download its CSV; reupload through instructor aggregator.
- [ ] Test mobile or smaller-screen projection readability and keyboard navigation.
- [ ] Keep v1.1 ZIP available as rollback if deployment fails.

## Reproduction

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py model.py classroom.py tests
python -m streamlit run app.py
```

Last line requires installing `requirements.txt` in a network-connected environment.

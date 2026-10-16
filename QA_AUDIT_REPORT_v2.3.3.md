# v2.3.3 QA / Release Audit

**Disposition: CONDITIONAL — source validation passes, browser acceptance outstanding.**

- Automated tests: 219 passed.
- Financial and GIS computational modules: source-byte identical to v2.3.2 (see release diff and SHA manifest).
- PDF generation: test-created PDFs parsed by `pypdf`, with checks for dates, quantitative figures and disclaimer wording.
- Python source compilation: tested at release build.
- Report values: drawn directly from `model.analyze()` outputs and saved `scenario_compare.compare()` summaries; no new financial formulas.
- Scope: reporting/UI only; existing projector toggle retained and clarified.
- Unverified: interactive Streamlit controls, PDF rendering in deployed browser, mobile responsiveness, and live GIS/Census data.
- Required live test: load different project assumptions, check project PDF metrics against Overview; save A/B snapshots with different allocations, export policy brief and reconcile both columns; toggle projector on/off; verify student PDF still works.
- Reports do not certify project feasibility, entitlement, eligibility or financing.

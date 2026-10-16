# DC Housing Lab v2.0.1 - Builder Remediation / QA Report

**Release disposition:** BUILDER TEST PASS / INDEPENDENT AUDIT PENDING. Not production approved.

## Evidence
- Local `python -m pytest -q tests`: **166 passed**.
- Python `compileall`: pass.
- Independent audit baseline: DC Housing Lab v2.0, 14 findings/limitations.
- Tested mocked GIS result sets including polygon hole/multipart, record-count conflict, out-of-polygon points, changed pagination counts, invalid fractional units, unsupported public debt, and negative terminal NOI.

## Material residual risks
1. This runtime cannot test the public Streamlit deployment. Actual layer schema and feature geometry might differ; the safe behavior is a warning instead of an invented map.
2. ArcGIS ring orientation assumptions are verified with synthetic fixtures; live boundary geometry must be checked.
3. Count stability does not imply exact snapshot stability when source records change without a changed count.
4. Financial coverage flags do not represent lender consent or automatically resize the requested public loan.
5. A nonpositive Year 11 NOI means terminal value is unavailable under this method, not zero market value.
6. Existing simplified developer cash-flow and public-subsidy limitations remain.

**Release gate:** All high-severity findings await independent reverification and live GIS/browser testing. No finding has been marked CLOSED by the Builder.

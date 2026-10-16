# DC Housing Lab v1.9.4 — Quality Control Audit

**Disposition: CONDITIONAL — local tests passed; hosted API integration still unverified.**

## Verification
- Python compilation: PASS.
- Regression and new reliability tests: **125/125 PASS** (`python -m unittest discover -s tests -q`).
- New cases include distinct-value discovery, case/punctuation aliases, unmatched source geography, record-count and pagination reconciliation, duplicate identifiers, invalid geography, partial unit completeness, verified zero, and source response failure.
- Underwriting: no changes to `model.py`, `forecast.py`, `public_policy.py`, `cash_flow.py`, `capital_stack.py` or other financial calculation modules.
- ZIP and package hashes verified after creation.

## Residual limitations / launch gates
1. **HIGH / Open:** Real DC GIS API endpoint behavior against the published service not exercised; validate source supports `returnDistinctValues` and `returnCountOnly` and that expected planning area and field values are present.
2. **HIGH / Open:** Hosted Streamlit click-through testing of the new diagnostics and all three neighborhoods not yet performed.
3. **MEDIUM / Open:** Independent server count does not guarantee a stable point-in-time snapshot if the GIS layer changes between count and page requests; count/duplicate checks reduce but do not eliminate this risk.
4. **MEDIUM / Known:** Planning-area project totals include diverse statuses and are not current affordable unit inventory. Unit sums can be partial where source values are missing.
5. **LOW / Known:** ACS tract data and selected neighborhood are not equivalent geographies.

Do not report this release as production-verified until a live GIS response and browser smoke test pass.

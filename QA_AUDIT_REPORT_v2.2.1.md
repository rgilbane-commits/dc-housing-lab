# DC Housing Lab v2.2.1 — Build QA / Audit Report

## Disposition: CONDITIONAL / NOT INDEPENDENTLY PRODUCTION-CERTIFIED

**Scope:** full source-based test suite; new per-allocation financing and operating screen; deployment package verification. **202/202 pytest tests passed.** Python compilation passed. Source hash manifest and ZIP integrity validated.

## Verified controls
1. Allocated grant used in a modeled project plus fractional uncommitted remainder reconciles to the allocated amount (subject to floating-point tolerance).
2. Capital screen uses the existing model's constrained private debt and required equity, not the user's full requested loan balance.
3. Operating screen measures reserve-adjusted NOI against combined debt service and requested minimum DSCR.
4. Model reports economic feasibility and funding sufficiency separately; all three screen components required for modeled pass.
5. Potential capacity is never presented as delivered or approved housing.
6. Zero-home, invalid input, over-budget, cross-strategy, oversized-project, and portfolio-total cases tested.
7. Existing regression suite continues to pass.

## Outstanding limitations / audit findings
- **OPEN HIGH — APP-001:** Hosted Streamlit click-through not tested; Streamlit is not installed in the build environment. Confirm controls and CSV download live.
- **OPEN HIGH — MODEL-001:** Per-home subsidy costs, rents, cost multipliers and unit mixes are hypothetical. No deal-specific project underwriting or agency qualification; a screen pass is *not* a financing commitment.
- **OPEN MEDIUM — MODEL-002:** Each allocation line is modeled as one project; >2,000 units cannot be screened. Portfolio totals describe illustrative results only.
- **OPEN MEDIUM — MODEL-003:** Reserve allowance is a single annual percentage of NOI. Long-term operating stability, preservation transaction viability, covenant terms, and lender-specific restrictions are not modeled here.
- **OPEN MEDIUM — DATA-001:** Sourced GIS/Census observations are contextual and are not used as market rent, land basis, transaction pipeline, subsidy sizing, or zoning inputs.

## Production smoke test checklist
- Open Public investment strategy; allocate $10M to one strategy and verify potential and screened homes are different concepts.
- Increase committed equity; check equity shortfall does not rise.
- Adjust requested private debt; confirm supportable private debt remains constrained by model.
- Set zero allocations; ensure no division or formatting errors.
- Over-allocate $100M; verify financial-screen output is withheld.
- Export feasibility CSV; verify numeric values and no claimed delivered homes.
- Recheck existing density bonus, mapping, and forecast controls.

## Audit status
Builder-authored validation only. Findings remain open for independent review and actual live-browser acceptance.

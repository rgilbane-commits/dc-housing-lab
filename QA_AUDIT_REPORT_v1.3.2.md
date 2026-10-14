# DC Housing Lab v1.3.2 — Quality Control Audit

**Disposition: PASS WITH LIMITATIONS — deploy and complete browser smoke test.**

## Scope
Retain v1.3.1 classroom simulation and financial corrections; add private permanent loan interest/amortization, minimum combined DSCR, maximum private LTV/LTC, debt capacity, amount of private debt modeled, required equity, and additional equity requirement. Carry new metrics into A/B comparison and proposal exports.

## Independent calculation checks
- Unlevered value and economic margin unaffected by changes in private loan amount.
- Sizing is the minimum of three distinct caps: (NOI / required combined DSCR − annual public loan payment) / private mortgage constant, property value × LTV, and net project cost × LTC; negative debt capacity is floored at zero.
- Private loan assumed advanced is the lesser of requested private debt and computed capacity; excess requested debt is flagged.
- Combined annual debt service = public + modeled private debt service; total DSCR = NOI / combined debt service (N/A when no debt).
- Required equity = max(0, net cost − grant − public loan − supportable private loan used). Additional equity required is floored at zero after subtracting the entered committed equity.
- Public loan service can crowd out private DSCR debt capacity, and a public loan alone may violate minimum DSCR; the app warns on that circumstance.

## Verification evidence
- **58/58 automated tests passed** using Python unittest, including 12 new private finance edge/regression tests.
- Python source and tests compiled successfully.
- Existing policy callback regression tests passed.
- Source deployment archive generated and ZIP integrity checked.

## Residual limitations
1. **LIVE-001 (deployment validation required):** Streamlit cannot be imported in this runtime; no deployed GUI interaction or hosting smoke test has been completed. Must be checked after GitHub deployment.
2. **MODEL-001:** Hypothetical classroom inputs; not actual loan quotes, AMI limits, or verified DC market data.
3. **MODEL-002:** Annual constant-payment amortizing loans; no construction-to-permanent transition, operating reserves, loan fees, interest-only periods, refinance tests, maturity balloons, restricted cash flow, subsidies with cash-flow-based repayment, or appraisal restrictions. Public-loan seniority/subordination is not modeled.
4. **MODEL-003:** Debt sizing assumes total NOI is available for combined service and simultaneously pays public and private loans; not a bank credit approval.
5. **MODEL-004:** The legacy committed-sources gap can differ from the capacity-adjusted equity shortfall when entered private debt exceeds supportable financing; both are intentionally labeled.
6. **UI-001:** Sidebar controls and classroom exports not visually tested on hosted Streamlit. Verify sliders, CSV download, scenario save/restore, and policy buttons after deployment.

## Deployment acceptance smoke tests
1. Load site, confirm v1.3.2 in header.
2. With default assumptions confirm private loan modeled at $30.0M and total DSCR about 1.57x.
3. Increase requested private debt to $100M: app should cap proceeds at supportable capacity and display a warning.
4. Increase public loan amount: unlevered stabilized value stays fixed; private debt capacity may decrease due to coverage constraint; total DSCR reflects both loans.
5. Set private LTV to 0%: no private debt proceeds; required equity increases.
6. Change neighborhood and select Load; sliders retain valid values. Recheck density bonus, land contribution, grants, and Reality Check callbacks.
7. Save Scenario A and B, export CSV, and inspect new debt/equity fields.

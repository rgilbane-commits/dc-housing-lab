# DC Housing Lab v2.2.0 — Builder QA Report

## Release disposition
Builder-tested, **conditional** pending hosted Streamlit browser smoke test. This is not an independent audit certification.

## Test execution
- `python -m unittest discover -s tests -p test*.py -q`: 134 tests passed.
- `python -m pytest -q`: see local test log; test count may differ by runner.
- `python -m compileall -q .`: passed.
- Source integrity: SHA256 manifest supplied.

## Financial and operational boundaries
- Allocations constrained to $100 million and validated finite/nonnegative.
- Gross allocations cannot exceed the cap; unallocated balance disclosed.
- Per-home public subsidy is a user-provided hypothetical assumption.
- Outputs represent *illustrative capacity*, not new units guaranteed, obligated or delivered.
- Repaid public loans are excluded from this capital-allocation engine; no false equivalence with grants.
- No claim of income-restricted eligibility, zoning, financing, operating cash flow or legally enforceable restrictions.
- The three attestation gates are supported by the pure model but are not displayed as attestable evidence in v2.2.0.

## Open verification
- Streamlit Cloud startup, responsiveness, slider/number-input interactions, CSV export and all legacy tab workflows.
- Live DC GIS / Census endpoint validation remains subject to v2.1.2 limitations.

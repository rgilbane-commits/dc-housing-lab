# DC Housing Lab v1.2.2 - Display Formatting QC

Disposition: PASS for automated source and model checks; live hosted browser smoke test remains outstanding.

Changes from v1.2.1:
- Added a centralized formatting module for money, percentages and unit counts.
- Corrected a sign-loss defect in prior compact dollar formatter (`abs()` removed negatives).
- Added comma separators and dollar signs in project, household, and instructor comparison tables.
- Kept stored numeric and CSV values unchanged so calculations and exports remain machine-readable.
- Updated UI version to v1.2.2. No underwriting equations, policy callbacks, or deployment dependencies changed.

QC performed:
- 28/28 unittest tests passed (prior tests plus 6 new formatting regressions).
- Python compilation passed.
- Package ZIP integrity check passed.

Limits and follow-up:
- The current container does not have Streamlit installed; no end-to-end hosted browser verification is claimed.
- Slider widgets show numerical values with contextual units in their labels; explicit thousands separators inside sliders may vary by Streamlit version. Model data tables and summary currency outputs are formatted.
- Table columns labeled $M use formatted values for presentation; exported CSV retains underlying numerical $M values.
- Model assumptions remain hypothetical and financial feasibility logic remains educational, not investment-grade.

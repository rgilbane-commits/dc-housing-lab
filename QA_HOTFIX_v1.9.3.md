# QA - v1.9.3

**Root cause:** DC GIS returned `FAR SOUTHEAST AND SOUTHWEST`; the application's exact filter used `FAR SOUTHEAST & SOUTHWEST`. v1.9.2 corrected letter case but not the conjunction.

**Correction:** Replace the planning-area query mapping for Congress Heights with the source literal. Validation requires the same area; unrelated area records remain rejected.

**Tests:** All local unit tests passed, including literal-filter and unrelated-area regression checks. Syntax and archive integrity verified. **Limitations:** Service response and live Streamlit UI were not verified by these mocked tests. No financial calculation changed.

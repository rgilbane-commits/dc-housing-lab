# DC Housing Lab v2.4.0 — Production Acceptance Audit

**Disposition: NOT APPROVED FOR PRODUCTION BASELINE FREEZE.**

## Scope
The v2.3.3 source was copied without changing the analytical model or Streamlit UI. This package is an **acceptance candidate and evidence kit**, not a completed deployment certification.

## Confirmed results
- 219 automated regression tests pass on the v2.3.3 source.
- Python source parses.
- Local PDF creation and text extraction succeed.
- Release manifest and ZIP CRC can be verified.

## Blocking evidence gaps
- Hosted Streamlit URL redirects to authentication; no authenticated visual browser QA.
- Streamlit and streamlit-folium not available in the local audit runtime; widget behavior and responsive rendering untested.
- Live official GIS and ACS integrations not validated end-to-end.
- CSV/PDF user download behavior not reconciled in browser.

## Risk notes
- Presentation mode is a CSS sidebar hide, not real programmatic fullscreen.
- Existing location and production ratio methodology remains approximate; no investment-policy certification is implied.
- App uses Streamlit internal data-testid CSS selectors; these may change between hosted Streamlit versions and require visual verification.
- Existing inline callback/session mutation paths warrant live tests after tab restructuring.

## Gate
Complete `LIVE_ACCEPTANCE_CHECKLIST.md`, attach browser evidence, remediate failures, and repeat regressions before assigning APPROVED / FROZEN status.

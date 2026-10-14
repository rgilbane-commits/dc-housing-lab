# Independent-style QC audit — DC Housing Lab v1.4

**Disposition: PASS WITH LIMITATIONS for source release; live cloud UI validation pending.**

## Scope
Visual-only update to v1.3.4, including dashboard styles, conceptual massing graphic, reconciled capital stack bars, SVG floating operating waterfall, and instructor presentation toggle. No new neighborhood data, changes to underwriting formulas, or GIS support.

## Verification performed
- 86 Python regression / visual-helper tests passed using `python -m unittest discover -s tests -q`.
- Python compilation succeeded for application and modules.
- All six financial/model helper modules (`model.py`, `classroom.py`, `upgrade.py`, `capital_stack.py`, `cash_flow.py`, `display_format.py`) are byte-identical to v1.3.4.
- Visual-helper checks cover zero and full affordable share, 50–500 units, multiple public/private financing structures, and sources/uses reconciliation.
- Layout includes responsive CSS and a minimum-width horizontally scrollable SVG waterfall to avoid unreadable compressed labels.
- Finance formatting uses the unchanged shared formatter; SVG values escape output.
- No database, network API, external JavaScript, or new Python runtime dependency introduced.

## Residual limitations and risks
1. **Open / deployment-blocking verification:** Streamlit is unavailable in the local test environment; no live browser/screen-size test or Streamlit widget integration test was performed. Test the deployed app prior to public presentation.
2. Conceptual massing assumes 20 units/floor; graphic cannot establish zoning-compliant height, site coverage, setbacks, or actual building geometry. At >360 units only the lower 18 graphic floors are shown, with a truncation notice.
3. CSS targets some Streamlit `data-testid` attributes that may change in future Streamlit releases; cosmetic fallback should remain legible.
4. Numbers and underwriting reflect classroom assumptions, not verified DC financial or affordability limits.
5. A/B comparison and scenario upload are unchanged; not synchronized across student sessions.
6. For small charts and constrained screens, the waterfall scrolls horizontally; teacher should test projector layout.

## Required post-deployment smoke test
- Check version v1.4 in the app header/footer.
- Toggle Presentation mode; building and both financial graphics should render and update.
- Change affordable share 0% -> 100%, total units 50 -> 500, and verify labels and conceptual floors.
- Apply density bonus, $10M grant and $10M land contribution; no session-state exception.
- Increase public loan and inspect unchanged NOI, changed debt service, and capital-stack allocations.
- Inspect charts on laptop and mobile; verify `$`, `%`, `×`, negative values, and no clipped legends.
- Export classroom proposals and waterfalls; confirm valid CSVs.

**This document does not certify live public deployment.**

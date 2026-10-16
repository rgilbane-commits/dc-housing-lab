# v2.4 Live acceptance checklist

Tester: __________  Date: __________  Deployment commit SHA: __________

**Do not mark production-approved without authenticated hosted-browser evidence.**

1. **Environment:** Record hosted URL, Streamlit/Python version, GitHub commit, viewport sizes, and data access permissions.
2. **Startup:** Confirm load with no exception, and exactly five workspaces. Capture screenshot.
3. **Navigation:** Visit Overview, Development Studio, DC Housing Explorer, Investment Strategy, and Presentation & Reports. Confirm state continuity.
4. **Project:** Record settings and Overview figures; reconcile NOI, net cost, DSCR, equity gap against detailed financial sections and development PDF.
5. **Interactive controls:** Test reset, density bonus, land contribution, grant, Reality Check, and neighborhood change; check for Streamlit widget-state exceptions.
6. **Investment:** Save Scenario A, alter assumptions, save Scenario B. Verify two distinct snapshots, correct charts and CSV/PDF reconciliations.
7. **Geographic:** Load 3 areas, GIS map/project markers, classified production/preservation and data-quality indicators; run Census denominators with valid secret and confirm source timestamps/coverage. Capture failing-source behavior too.
8. **Exports:** Verify student PDF, development PDF, A/B brief, capital stack CSV, forecast CSV, geographic CSV; reconcile at least three amounts per export and verify missing/invalid values.
9. **Visual:** At widths 1440, 1024, 768, 390 px, inspect tab wrapping, charts, overflow, button labels, source indicators. Test projector mode and keyboard access.
10. **Privacy/accessibility:** Verify no API secrets in HTML/downloads/logs and keyboard focus/contrast on primary flows.
11. **Closeout:** Attach screenshots, issue logs, console traces, and signed acceptance. Re-run tests against deployed commit.

Disposition rules: any materially inconsistent financial figure, silent geographic-data substitution, fatal navigation bug, or exposed secret = BLOCK RELEASE.

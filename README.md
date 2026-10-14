# DC Housing Lab v1.5 - Deployment

## Upgrade from v1.4

1. Extract `DC_Housing_Lab_v1.5_Deploy.zip`.
2. Open your existing `dc-housing-lab` GitHub repository on the deployed `main` branch.
3. Upload the extracted files and directories **to the repository root** (not an extra folder), replacing matching files. Include the two new modules `neighborhood_map.py` and `student_report.py` and the updated `requirements.txt`.
4. Commit; Streamlit Cloud should rebuild and install the new dependencies.
5. Confirm the app footer says **v1.5**. If dependency updates are not reflected, open the Streamlit app menu and reboot.

## New v1.5 features

- **Policy lab / street map:** A Folium street map with three *approximate neighborhood-center markers*. Click a marker to load that neighborhood's **illustrative** baseline assumptions. The map requires an internet connection for map tiles. This is not a parcel-level zoning map, rent survey, or neighborhood demographic data layer.
- **Presentation mode:** Toggle at the top of the app to hide the sidebar and enlarge the main content. Use **F11** (Windows) to make your browser full-screen. Turn the toggle off to restore the sidebar. The instructor tab contains building massing, capital stack, and operating waterfall.
- **Student summaries:** In Classroom challenge, choose a team name and priority then download a **one-page PDF** for the current housing and financing scenario. The PDF includes homes, affordability, net development costs, grants, public and private debt, equity, DSCR, NOI, stabilized cash flow, return proxy, and discussion prompts.

## Included files

`app.py`, `model.py`, `classroom.py`, `upgrade.py`, `cash_flow.py`, `capital_stack.py`, `display_format.py`, `visuals.py`, `neighborhood_map.py`, `student_report.py`, `requirements.txt`, `tests/`, `README.md`, and `QA_AUDIT_REPORT_v1.5.md`.

## Verification steps on the public URL

1. Click **Congress Heights** on the Policy lab map. Confirm the sidebar selection and default rents/costs update (the existing custom case is replaced by the selected neighborhood baseline).
2. Click **Friendship Heights** and verify the map moves its selected marker and values change.
3. Turn on **Presentation mode**, confirm sidebar disappears, then use F11 and inspect the charts. Switch presentation mode off to restore controls.
4. Under **Classroom challenge**, download and open a PDF; ensure it is one page and figures match the current dashboard.
5. Regression-check **Apply density bonus**, **Apply grant**, private debt capacity, and the cash-flow waterfall.

## Known limitations

- Current development inputs and affordability labels remain **illustrative**, not verified DC data or regulatory income limits.
- Map locations are neighborhood approximations; map tiles come from third-party online providers. No geocoding API keys or user-location permissions are needed.
- The 'presentation mode' is CSS-based; F11 is needed for true browser full-screen.
- This package passed unit/regression and generated-PDF visual tests but **was not live-browser tested** in the deployed Streamlit environment. The new Folium integration therefore requires a hosted smoke test.
- Student downloads are per-browser-session. This is not an online multiplayer service.


## v1.5.1 map hotfix
Switched the Folium background tile source to OpenStreetMap (no API key required). Clickable neighborhood markers and existing map-selection handling are preserved. Map imagery still requires internet access, and tile accessibility depends on the network/provider. No model calculations changed.

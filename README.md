# DC Housing Lab v2.3.3 — Presentation & Policy Reporting

## Deploy
Upload the contents of this ZIP to the existing Streamlit GitHub repository (not the parent folder). Preserve `requirements.txt` and all modules; new module: `policy_brief.py`. Commit and let Streamlit redeploy.

## Use
Visit **Presentation & Reports**. Toggle projector mode at the top for simplified classroom display (browser F11 for full screen). Download the development brief from the active project. To download the investment policy brief, first save Scenarios A and B in **Investment Strategy**; return to Presentation & Reports. Both reports are generated from the active session values.

## Verification
Run `python -m pytest -q tests` inside the extracted folder. Local tests verify PDF parseability and content; actual Streamlit browser interaction must be verified after deployment. Confirm PDF export matches displayed figures, especially when inputs and saved scenarios change. No independent live-browser validation has been conducted.

## Limitations
These reports are classroom decision aids; estimated homes and financing screen passes are not commitments or delivered projects. PDF data as-of is generation time, and geographic/ACS contextual estimates remain subject to previously documented qualification. Projector mode uses CSS and does not programmatically invoke browser full-screen.

# DC Housing Lab v1.4 — Visual Upgrade

Upgrade from v1.3.4. Streamlit app with improved responsive styling, conceptual building massing, reconciled sources-and-uses bars, a floating cash-flow waterfall, and a presentation-mode toggle. No model formulas were changed.

## Deploy
Upload the **contents** of this folder to the GitHub repository root, replacing existing files and adding `visuals.py`. Ensure `app.py`, `model.py`, `classroom.py`, `capital_stack.py`, `cash_flow.py`, `upgrade.py`, `display_format.py`, `visuals.py`, and `requirements.txt` are present. Streamlit Community Cloud entrypoint: `app.py`.

## Run locally
`pip install -r requirements.txt` then `streamlit run app.py`. Run regression tests with `python -m unittest discover -s tests -v`.

## Important assumptions
Building floors assume 20 units per floor purely for illustration and are not zoning-compliant massing. App finances and household incomes are hypothetical. Charts use the existing calculation outputs; the sources bar omits unused commitments and shows remaining equity. The waterfall is a single stabilized representative year.

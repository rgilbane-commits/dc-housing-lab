# DC Housing Lab v2.2.0 — Public Investment Allocation Engine

Deploy all extracted files to the root of the existing GitHub repository. Streamlit entry point: `app.py`.

## Scope

Adds **Public investment strategy** tab with $100M cap, 3 planning areas, 4 housing strategies, editable assumed public support per home, unallocated budget warnings, illustrative potential units and raw CSV export. No project is counted as delivered. Existing financial engine is retained.

**Important:** Per-home figures are hypothetical instructional parameters; they are not verified DC grant cost or full development costs. No live API is needed for the allocation tab. Public repayable loans intentionally excluded from capital allocation (not equivalent to a grant).

## QA and deployment

Run `python -m unittest discover -s tests -p 'test*.py'` from application root; test dependencies may require `pip install -r requirements.txt`. Deploy to Streamlit and test the new tab, export, budget cap, and old financial controls. Browser smoke test is pending until deployed.

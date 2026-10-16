# DC Housing Lab v1.9.2 — DC GIS planning-area case hotfix

Upload all application `.py` files, `requirements.txt`, data CSV files, and `tests/` to the root of the existing GitHub repo. Commit to the deployed branch and refresh Streamlit.

## Fix
The DC GIS `PLANNING_AREA` attribute uses uppercase values. v1.9.1 issued an exact comparison using title-case labels, causing valid planning areas to appear empty. v1.9.2 queries the uppercase values and compares response names case-insensitively. Empty-result protection remains enabled. No financial formulas were modified.

## Validation
Run `python -m unittest discover -s tests -p 'test*.py' -q` from the repository root. 115 tests passed in the build environment. Live DC GIS results still require hosted validation.

## Smoke test
In the app's Policy Lab, select Friendship Heights, refresh public data, and inspect Rock Creek West count and sample project records. Repeat for Columbia Heights and Congress Heights. Ensure return values and geographic labels are correct. If zero or an API error persists, capture the diagnostic message and Streamlit logs.

## Scope
These are projects started or completed since 2015 in entire DC planning areas, not current affordable unit availability or exact neighborhood inventories.

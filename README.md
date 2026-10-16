# DC Housing Lab v1.9.3 - DC GIS literal-value hotfix

Fixes the Congress Heights planning-area filter to query `FAR SOUTHEAST AND SOUTHWEST`, the spelling returned by the live DC GIS service, rather than `FAR SOUTHEAST & SOUTHWEST`. The accepted result is validated against the same canonical string. No financial formulas or mappings for the other two neighborhoods were changed.

## Deploy
Upload the extracted files to the existing GitHub repository root, including `live_data.py` and `app.py`. Commit to the Streamlit-connected branch. Open Policy Lab > Live DC neighborhood evidence, select Congress Heights, and press Refresh public data now. A positive retrieved result must be checked against the official GIS records; an empty result should still be treated as unverified.

## QA
Run `python -m unittest discover -s tests -p 'test_*.py'` from the repository root. Tests use mocked service responses; real GIS retrieval must be checked after deployment.

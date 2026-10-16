# DC Housing Lab v2.3.2
Full Streamlit application. Deploy by replacing matching files in the existing GitHub repository, including `geographic_visuals.py`; retain `requirements.txt` and `tests/`.

Navigate to **DC Housing Explorer**. Under **Geographic Housing Intelligence**, choose **Analyze all three planning areas** to populate the dashboard. Activate the official boundary map separately using its checkbox. The grouping chart shows numbers only for fully classified source datasets; empty columns are *not* zero.

## Acceptance gates
1. Browser-load all five workspaces and run official map after fresh GIS retrieval.
2. Check three-area chart and source completeness vs underlying live GIS records.
3. Verify Census denominators, missing-data states, and exports.
4. Confirm project financial and investment pages remain unchanged.

Live Streamlit/browser and network GIS tests were not run here; approve only after hosted validation.

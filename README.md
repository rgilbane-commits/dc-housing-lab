# DC Housing Lab v1.9.4 — GIS Reliability Release

Upload all files and the `tests/` folder into the root of your existing GitHub repository, replacing matching files. Streamlit continues to start from `app.py`. Financial model files are retained.

## Improvements
- Discovers the GIS layer's actual distinct `PLANNING_AREA` values before querying.
- Normalizes case, whitespace, punctuation, and `&` versus `AND`; refuses unmatched or ambiguous geography.
- Uses the exact returned source value for the filter.
- Requests an independent server count and verifies that all paginated records were received.
- Rejects duplicates, wrong-geography rows, malformed responses, and incomplete pagination.
- Reports missing affordable-unit counts as missing; no implicit zeros.
- Shows status, retrieval time, reported-unit completeness, and reconciliation count.
- Preserves optional Census functionality, source links, and hypothetical underwriting.

## Deploy / smoke test
1. Upload extracted contents to `rgilbane-commits/dc-housing-lab` and commit on `main`.
2. Visit the existing Streamlit app; hard refresh. Confirm v1.9.4 in UI.
3. Choose Friendship Heights, Columbia Heights, and Congress Heights, refreshing each time in Policy Lab.
4. Confirm planning-area names and source count vs loaded records. When data fail, check for a warning rather than a green zero.
5. Re-test density bonus, capital stack, waterfall, and student PDF download.
6. Keep v1.9.3 as a rollback release until hosted live verification succeeds.

## Requirements and limitations
No new Python dependencies. The GIS endpoint must support ArcGIS REST distinct-value and count queries. Live service behavior and deployed Streamlit/browser rendering could not be verified from this environment. Results are planning-area projects, not current affordable housing inventory or neighborhood-only homes. Census results are for a single tract containing the map reference point. No API key is needed for the GIS endpoint; the Census API requires separately configured credentials.

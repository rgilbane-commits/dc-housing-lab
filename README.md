# DC Housing Lab v2.0.1 - Audit remediation

Deploy: extract this package into the root of the existing GitHub repository and commit to the Streamlit-connected branch. Ensure `geo_policy.py`, `live_data.py`, `model.py`, `forecast.py`, `app.py`, and `requirements.txt` are updated together. A new dependency, Shapely, is installed via `requirements.txt`.

## Corrections
- Topology-aware GIS planning-area GeoJSON preserving exterior rings, holes, and multipart areas.
- Boundary record fetched by source OBJECTID with exact count check. The neighborhood reference point must fall in the returned polygon.
- Project markers must fall inside their assigned polygon; any spatial mismatch suppresses the entire geospatial map rather than silently dropping rows.
- Public loan feasibility evaluated against minimum total DSCR; loan request is not silently represented as approved financing.
- Negative/zero Year 11 NOI makes income-capitalization terminal valuation and associated sale-based equity returns unavailable.
- Whole nonnegative unit count validation; GIS pre/post page count reconciliation to flag changing result sets.

## Remaining limitations
- The public loan principal entered is still a requested assumption; it is not automatically capped to a lender-approved amount. The app explicitly flags unsupported configurations.
- Count-before/count-after detects count changes, but not record replacements that leave the same count. No transactional GIS snapshot is available.
- Live GIS, map tile, and Streamlit browser testing is still REQUIRED after deployment. 166 source and mocked-service tests passed locally; that is not production approval.
- This tool is educational and is not suitable for authoritative siting, policy allocation, or investment underwriting.

## Required live acceptance
1. Select each of the 3 neighborhoods and open the live geospatial map.
2. Confirm correct boundary and project markers; inspect warnings for spatial mismatches.
3. Test GIS outage and map tile unavailability.
4. Enter an excessively large public loan and confirm financing warning.
5. Force negative Year 11 NOI using adverse growth assumptions; verify N/A exit and IRR.
6. Test the density-bonus callback, capital stack, CSV export, PDF export, and mobile/projector layouts.
7. Verify that the deployed Git commit corresponds to the release files.

# v2.0.1 Change log

- GEO-001: Replaced independent filled rings with ArcGIS ring-orientation-based topology geometry and Folium GeoJSON.
- GEO-002: Added strict point-in-polygon verification and fail-closed map suppression for mismatches.
- GEO-003: Added OBJECTID-based boundary query with exact returned record count validation.
- FIN-001: Added public-loan DSCR viability flag and explicit UI warning; requested proceeds remain an assumption.
- FIN-002: Suppressed terminal capitalization and exit-based return metrics if Year 11 NOI <= 0.
- DATA-001: Excluded invalid or fractional affordable unit values from aggregated totals.
- DATA-002: Added post-pagination count check; not an atomic snapshot.
- DATA-003: Confirmed reference point containment by official polygon (live verification outstanding).
- APP-002: Expanded geospatial render fallback to catch unexpected runtime failures.
- QA-001: Added focused regression tests; hosted smoke verification remains outstanding.
- Legacy source hash test updated to correspond to the authorized model.py change.

No Builder finding is marked independently CLOSED.

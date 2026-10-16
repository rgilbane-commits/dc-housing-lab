# DC Housing Lab v1.9.1 - GIS Empty Result Guard

## Observed user defect
In the DC GIS panel, `status=empty` and three zero metrics were rendered as a green success even though the filtered ArcGIS query returned no matching records. This does not establish a zero affordable-housing project count.

## Changes
- Retains original planning-area filter and project-count calculation for nonempty valid responses.
- On an empty response, issues an independent paginated `1=1` source query and inspects actual PLANNING_AREA values.
- If no records match, raises an explicit DataUnavailable message with example area names; the UI already renders this as warning and suppresses all three zero-valued metrics.
- Updates version label to v1.9.1. Underwriting logic unchanged.

## Verification
- 112 unit tests passed, including 3 new zero-result regression tests.
- Python compilation successful.
- ZIP integrity checked separately.
- Official live ArcGIS schema inspected: FeatureServer layer 62 includes PLANNING_AREA, OBJECTID and TOTAL_AFFORDABLE_UNITS.

## Limitations / residual risks
- A no-match result remains unverified, not auto-corrected to another planning-area label. User must review actual values and geographic boundaries.
- This environment cannot make direct HTTPS requests to the public ArcGIS endpoint, and no live Streamlit browser run was performed. Hosted smoke test required.
- A planning-area aggregate is not a neighborhood-specific inventory.

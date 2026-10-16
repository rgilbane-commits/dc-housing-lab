# DC Housing Lab v1.9 — QA Audit Report

**Disposition: Source/regression PASS; hosted integration PENDING.**

## Executed

- 109 automated tests passed (`python -m unittest discover -s tests -q`).
- Python compilation passed (`python -m compileall -q .`).
- Existing six financial calculation modules match v1.8 byte-for-byte (SHA-256 regression test).
- DC GIS parser tests: populated/missing unit fields, duplicate project IDs rejected, pagination shape, correct planning-area selection, network failures and mismatched geographies.
- Census tests: missing API key, tract-geocoder response, valid income/MOE, sentinel handling and malformed response.
- Absent/failed public endpoints do not replace verified historical evidence with invented data.
- Required API key is never embedded in app source or package.

## Open verification items

1. This environment cannot reach `maps2.dcgis.dc.gov` or Census live HTTPS services, so **no live provider response was verified**.
2. Cloud browser and Streamlit UI were **not** tested in a hosted session.
3. GIS layer naming, data field values, provider availability and Census tract geocoder mappings may change.
4. Planning-area housing projects and selected-point Census tracts are not neighborhood-wide inventory or market-rent datasets.

## Limitations

- GIS is an official public projects layer describing starts or completions since 2015; statuses may differ and the sum is not available affordable units.
- ACS income is a five-year tract estimate, not DC HUD area median income; data may be suppressed or subject to MOE.
- Source query time limits, maximum pagination, and explicit unavailable states are preferable to partial or misleading results.
- All underwriting remains hypothetical. Prior historical evidence is retained and date-labeled.

## Deployment acceptance

Validate the five checks in README.md before designating the hosted release fully approved. Previous v1.8 package remains the fallback.

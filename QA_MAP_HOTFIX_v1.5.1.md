# DC Housing Lab v1.5.1 - Map hotfix verification

- Reported issue: interactive map displays an API-key requirement.
- Change: CartoDB Positron replaced with OpenStreetMap tiles in `neighborhood_map.py`.
- No third-party API key or Mapbox token is required by this implementation.
- Neighborhood click event and selection logic retained.
- Financial calculation modules unchanged.
- Limitations: Online map tiles still require internet access; browser deployment remains to be checked on Streamlit Cloud. An API-key error originating from another app version or cached hosting configuration may require checking Streamlit logs.

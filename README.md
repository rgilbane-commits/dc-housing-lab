# DC Housing Lab v1.9 — Live Public Data (optional)

Complete replacement package for the v1.8 Streamlit app. Upload the **contents** of this folder to the root of the existing GitHub repository, including `live_data.py`, the updated `app.py`, and `requirements.txt`. Streamlit will redeploy on commit.

## Using the new evidence panel

In **Policy Lab**, scroll to **Live DC neighborhood evidence**. It automatically requests DC GIS affordable housing project records for the **planning area** associated with your selected neighborhood. Press **Refresh public data now** to clear the 24-hour application cache and refetch. If the endpoint is unavailable, the app displays a warning and retains the historical 2018 context. It does **not** substitute the historical counts for current live statistics.

DC GIS feature layer: https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/FeatureServer/62

### Census ACS (optional)

Census documents an API key requirement. Obtain a key from https://api.census.gov/data/key_signup.html and, in Streamlit Cloud **Manage app → Settings → Secrets**, add:

```toml
CENSUS_API_KEY = "YOUR_CENSUS_API_KEY"
```

Do not commit the key to GitHub. Without it, the rest of the app operates normally. ACS values are for the **single 2024 ACS Census tract** containing the selected neighborhood's approximate map marker, not for the neighborhood as a whole. The income statistic uses table B19013 (2024 ACS 5-year) and retains its margin of error. 2024 dollar basis; source https://api.census.gov/data/2024/acs/acs5.

### Geographic methodology

* Friendship Heights → Rock Creek West planning area; marker (38.9593,-77.0847).
* Columbia Heights → Mid-City planning area; marker (38.9289,-77.0327).
* Congress Heights → Far Southeast & Southwest planning area; marker (38.8437,-76.9889).

GIS projects include starts **or** completions since 2015, production **and** preservation. The sum of project-reported units is **not** a current available/occupied inventory, net new homes, or completions. Missing unit fields are flagged, not imputed to zero. 2024 ACS median income is a sample estimate for a tract with its own statistical error.

### Constraints and reliability

- Source URLs are fixed to official DC GIS / Census endpoints. Timeout and response-schema checks prevent silently passing malformed data.
- GIS data are paginated and checked for unique `OBJECTID`, valid planning-area matches, and missing unit counts.
- Live observations are **display only**; they do not alter scenario rents, costs, debt, zoning, or affordability assumptions.
- 24-hour cache reduces API load; refresh clears the cache.
- Streamlit Cloud must be allowed to connect to the public services. A key is required only for Census, not for DC GIS. Neither live endpoint was accessible from the package-building environment, so hosted live responses must be checked.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
python -m unittest discover -s tests -q
```

## Post-deployment checks

1. Open **Policy Lab**, confirm GIS loads or presents a clear unavailable message, and verify its planning area is correct.
2. Set optional `CENSUS_API_KEY` in Streamlit secrets, refresh, and verify the ACS tract and income/MOE. If absent, ensure the app still works.
3. Change the neighborhood and verify GIS geography updates, while financial assumptions change only through existing scenario controls.
4. Exercise density bonus, capital stack, annual waterfall, and student PDF download.
5. Verify tabs and presentation view on laptop and projector screens.

The app is for educational use, not investment underwriting or live housing availability decisions.

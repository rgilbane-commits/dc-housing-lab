# DC Housing Lab v2.4.1 Citywide Geography

Deploy application files over the prior release. The Neighborhood selector now provides representative points for all eight wards and covers **all ten DC Comprehensive Plan planning areas**.

The GIS project filters and Census geographic denominators remain based on **planning areas**, which do not match ward boundaries. Ward references do not make GIS totals ward statistics. New 2018/2019 figures are not fabricated; unverified values display as unavailable.

The public investment strategy module continues to cover its original three planning areas; expanding it to all ten is a separate future change.

Run `python -m pytest -q tests` from the application root, then verify browser navigation, each of the 10 GIS boundaries, Citywide comparison, and exports in authenticated Streamlit. External API access is required for live testing.

Sources: https://planning.dc.gov/publication/area-elements-map ; https://planning.dc.gov/am/page/comprehensive-plan-and-center-city-related-area-elements

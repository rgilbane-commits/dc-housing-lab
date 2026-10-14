# DC Housing Lab v1.8 | Evidence Desk

Upload the contents of this ZIP to your existing GitHub repository (branch `main`). Include the **new** `evidence.py` module. Entrypoint: `app.py`.

## New: DC evidence desk in Policy lab

- Historical **2018 affordable housing inventory** at the DC *planning-area* level; clearly distinct from neighborhood/ward data.
- **2025 additional affordable housing production goals**, established in the 2019 Housing Equity Report. These are targets, not achieved units.
- Confirmed District housing production milestone: **36,216 homes as of July 29, 2024**. This is NOT a current October 2026 count.
- Links to official DC OP ACS Data Hub, DC GIS Affordable Housing layer and housing tracker for further investigation.
- Auditable in-app/source-register CSV with reporting period and precise geographic unit for each record.
- **All development rents, costs, AMI example amounts, density and financing assumptions remain illustrative and unchanged.** No inference of current neighborhood rents or unit counts.

## Classroom prompts

1. Why did Rock Creek West have 470 dedicated affordable units in the 2018 planning-area inventory, while Far Southeast & Southwest had 15,760?
2. Why is a goal for new affordable units not the same as an existing housing inventory?
3. Should the public maximize units, distribute access to opportunity, or preserve existing affordability?

## QA

Run `python -m pytest -q tests` and `python -m py_compile app.py evidence.py`. Live browser verification of map and source panel remains necessary after Streamlit deployment.

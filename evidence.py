"""Auditable public DC housing context; NEVER substituted into illustrative underwriting."""
from dataclasses import dataclass

HOUSING_EQUITY_URL = "https://housing.dc.gov/sites/default/files/dc/sites/housingdc/page_content/attachments/Housing%20Equity%20Report%2010-15-19.pdf"
PRODUCTION_URL = "https://dc.gov/release/mayor-bowser-and-community-members-mark-significant-milestone-36000-new-homes-2025-0"
CENSUS_URL = "https://opdatahub.dc.gov/"
PROJECTS_URL = "https://maps2.dcgis.dc.gov/DCGIS/rest/services/DCGIS_DATA/Property_and_Land/MapServer/62"
HOUSING_TRACKER_URL = "https://housing.dc.gov/page/housing-tracker"

# Figures are for District PLANNING AREAS, not their constituent neighborhoods.
# 2018 EXISTING dedicated affordable units; 2019 REPORT's 2025 additional-unit targets.
PLANNING_AREAS = {
    "Friendship Heights / Ward 3": {"area":"Rock Creek West", "existing_2018":470, "target_2025":1990},
    "Columbia Heights / Ward 1": {"area":"Mid-City", "existing_2018":6960, "target_2025":1010},
    "Congress Heights / Ward 8": {"area":"Far Southeast & Southwest", "existing_2018":15760, "target_2025":1120},
}

SOURCES = [
    {"id":"DC-HE-2019", "title":"DC Housing Equity Report (2019)", "url":HOUSING_EQUITY_URL,"observation_period":"2018 housing inventory / goals set in 2019 for 2025", "geography":"DC planning areas", "status":"Historical baseline, not current inventory"},
    {"id":"DC-PROD-2024", "title":"DC Mayor housing production announcement (July 29, 2024)", "url":PRODUCTION_URL,"observation_period":"2019 through July 29, 2024", "geography":"Districtwide", "status":"Historical announced count, not current production"},
    {"id":"DC-OP-ACS", "title":"DC Office of Planning Demographic Data Hub", "url":CENSUS_URL,"observation_period":"2020-2024 ACS 5-year estimates on hub", "geography":"Multiple geographies (check each download)", "status":"Linked reference; no unsourced tract-level figures imported"},
    {"id":"DC-GIS-AFF", "title":"DC GIS Affordable Housing feature layer", "url":PROJECTS_URL,"observation_period":"Projects started or completed since Jan 2015; check record update dates", "geography":"Geocoded projects", "status":"Linked feature layer; not counted in local snapshot"},
    {"id":"DC-HOUSING-TRACK", "title":"DC Housing Tracker", "url":HOUSING_TRACKER_URL,"observation_period":"Online tracker; check displayed update", "geography":"Districtwide", "status":"Linked dashboard; no automatic live import"},
]

def planning_area_context(neighborhood):
    data=PLANNING_AREAS[neighborhood].copy()
    data.update({"selected_neighborhood":neighborhood, "source_id":"DC-HE-2019", "source_url":HOUSING_EQUITY_URL, "existing_as_of":2018,"target_document_year":2019,"target_year":2025})
    return data

def district_production():
    return {"delivered_units":36216,"as_of":"2024-07-29","geography":"District of Columbia", "source_url":PRODUCTION_URL}

def records():
    return list(SOURCES)

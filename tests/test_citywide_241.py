from model import NEIGHBORHOODS, neighborhood_inputs, analyze
from live_data import CENTERS
from geo_policy import AREA_NAMES
from evidence import PLANNING_AREAS, planning_area_context

def test_all_wards_represented():
    assert all(any(f"Ward {i}" in name for name in NEIGHBORHOODS) for i in range(1,9))

def test_all_ten_planning_areas_unique():
    assert len(NEIGHBORHOODS)==10
    assert len({x.casefold() for x in AREA_NAMES.values()})==10
    assert set(NEIGHBORHOODS)==set(CENTERS)==set(AREA_NAMES)==set(PLANNING_AREAS)
    assert all(CENTERS[n][2]==AREA_NAMES[n] for n in NEIGHBORHOODS)

def test_every_reference_underwrites_without_unsupported_data():
    for name in NEIGHBORHOODS:
        r=analyze(neighborhood_inputs(name))
        assert r['gross_cost']>0 and r['noi']>0

def test_unverified_historical_fields_are_explicitly_missing():
    assert planning_area_context('Brookland / Ward 5')['existing_2018'] is None
    assert planning_area_context('Downtown / Ward 2')['target_2025'] is None

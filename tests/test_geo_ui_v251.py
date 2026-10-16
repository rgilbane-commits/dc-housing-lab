from geography_ui import sorted_reference_locations, area_rows, ward_number
from model import NEIGHBORHOODS

def test_sorted_by_ward_then_name():
    names=sorted_reference_locations(NEIGHBORHOODS)
    assert [ward_number(x) for x in names] == sorted(ward_number(x) for x in names)
    assert names[0].endswith('Ward 1')
    assert names[-1].endswith('Ward 8')
    assert names.index('Downtown / Ward 2') < names.index('Dupont Circle / Ward 2')

def test_unique_alphabetical_planning_areas():
    rows=area_rows(NEIGHBORHOODS)
    names=[x['DC planning area'] for x in rows]
    assert len(names)==len(set(names))==10
    assert names==sorted(names,key=str.casefold)
    assert rows[0]['DC planning area']=='Capitol Hill'

def test_historical_figures_unchanged_and_missing_not_zero():
    data={row['DC planning area']:row for row in area_rows(NEIGHBORHOODS)}
    assert data['Rock Creek West']['Existing affordable units (2018)']==470
    assert data['Mid-City']['Existing affordable units (2018)']==6960
    assert data['Central Washington']['Existing affordable units (2018)'] is None

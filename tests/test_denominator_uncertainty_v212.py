import math
import pytest
from shapely.geometry import box, mapping
from geo_denominators import parse_acs,aggregate,DenominatorUnavailable

HEAD=['B11001_001E','B25001_001E','B11001_001M','B25001_001M','state','county','tract']

def test_acs_moe_parse():
    assert parse_acs([HEAD,['100','120','20','30','11','001','000100']])['11001000100']==(100,120,20,30)

def test_acs_bad_moe():
    with pytest.raises(DenominatorUnavailable):parse_acs([HEAD,['100','120','-1','30','11','001','000100']])

def test_moe_aggregation_exact_boundary():
    b=box(-77.05,38.89,-77.03,38.91)
    d=aggregate({'geojson':mapping(b)},{'11001000100':b},{'11001000100':(100,120,20,30)})
    assert math.isclose(d['households_moe_90_proxy'],20,rel_tol=1e-6)
    assert math.isclose(d['housing_units_moe_90_proxy'],30,rel_tol=1e-6)

def test_legacy_missing_moe_shows_unknown():
    b=box(-77.05,38.89,-77.03,38.91)
    d=aggregate({'geojson':mapping(b)},{'11001000100':b},{'11001000100':(100,120)})
    assert d['households_moe_90_proxy'] is None

def test_duplicate_overlapping_tract_rejected():
    b=box(-77.05,38.89,-77.03,38.91)
    with pytest.raises(DenominatorUnavailable,match='Overlapping'):
        aggregate({'geojson':mapping(b)}, {'11001000100':b,'11001000200':b}, {'11001000100':(100,120),'11001000200':(100,120)})

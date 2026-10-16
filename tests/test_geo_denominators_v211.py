import pytest
from shapely.geometry import box,mapping
from geo_denominators import parse_acs,aggregate,DenominatorUnavailable

def test_parse_acs_valid():
    p=[['B11001_001E','B25001_001E','state','county','tract'],['120','150','11','001','000100']]
    assert parse_acs(p)=={'11001000100':(120,150)}

@pytest.mark.parametrize('row', [['-1','3','11','001','000100'],['10','8','11','001','000100'],['x','20','11','001','000100']])
def test_bad_acs(row):
    with pytest.raises(DenominatorUnavailable):parse_acs([['B11001_001E','B25001_001E','state','county','tract'],row])

def test_area_weighted_exact_geometry():
    boundary={'geojson':mapping(box(-77.05,38.89,-77.03,38.91))}
    tracts={'11001000100':box(-77.05,38.89,-77.03,38.91)}
    result=aggregate(boundary,tracts,{'11001000100':(1000,1300)})
    assert abs(result['households_est']-1000)<1e-5
    assert abs(result['housing_units_est']-1300)<1e-5
    assert result['coverage']>.9999

def test_missing_tract_rejected():
    boundary={'geojson':mapping(box(-77.05,38.89,-77.03,38.91))}
    with pytest.raises(DenominatorUnavailable):aggregate(boundary,{'11001000100':box(-77.05,38.89,-77.03,38.91)},{})

def test_partial_geometry_rejected():
    boundary={'geojson':mapping(box(-77.05,38.89,-77.03,38.91))}
    with pytest.raises(DenominatorUnavailable):aggregate(boundary,{'11001000100':box(-77.05,38.89,-77.04,38.91)},{'11001000100':(100,200)})

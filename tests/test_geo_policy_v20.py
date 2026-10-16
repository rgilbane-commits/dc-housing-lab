from unittest.mock import patch
import pytest
from shapely.geometry import shape, Point
from geo_policy import boundary_geometry,project_points,_geometry
from live_data import DataUnavailable

def test_polygon_hole_and_multi():
    shell=[(-77.12,38.92),(-77.12,38.99),(-77.02,38.99),(-77.02,38.92),(-77.12,38.92)]
    hole=[(-77.09,38.94),(-77.07,38.94),(-77.07,38.96),(-77.09,38.96),(-77.09,38.94)]
    poly=_geometry([shell,hole])
    assert poly.covers(Point(-77.11,38.95)) and not poly.covers(Point(-77.08,38.95))
    shell2=[(-77.21,38.92),(-77.21,38.94),(-77.19,38.94),(-77.19,38.92),(-77.21,38.92)]
    assert _geometry([shell,shell2]).geom_type=='MultiPolygon'

def test_boundary_identifier_count_reconcile():
    shell=[[-77.12,38.92],[-77.12,38.99],[-77.02,38.99],[-77.02,38.92],[-77.12,38.92]]
    responses=[{'features':[{'attributes':{'OBJECTID':5,'NAME':'ROCK CREEK WEST'}}]}, {'count':1}, {'features':[{'attributes':{'OBJECTID':5,'NAME':'ROCK CREEK WEST'},'geometry':{'rings':[shell]}}]}]
    with patch('geo_policy.get_json',side_effect=responses) as get:
        result=boundary_geometry('Friendship Heights / Ward 3')
        assert shape(result['geojson']).covers(Point(-77.0847,38.9593))
        assert get.call_count==3

def test_boundary_rejects_wrong_count():
    responses=[{'features':[{'attributes':{'OBJECTID':5,'NAME':'ROCK CREEK WEST'}}]}, {'count':2}]
    with patch('geo_policy.get_json',side_effect=responses):
        with pytest.raises(DataUnavailable):boundary_geometry('Friendship Heights / Ward 3')

def test_project_outside_boundary_rejected():
    shell=[(-77.12,38.92),(-77.12,38.99),(-77.02,38.99),(-77.02,38.92),(-77.12,38.92)]
    boundary={'geojson':_geometry([shell]).__geo_interface__}
    with pytest.raises(DataUnavailable):project_points({'rows':[{'OBJECTID':1,'LATITUDE':38.95,'LONGITUDE':-76.99}]},boundary)

def test_project_points_missing():
    assert project_points({'rows':[{'LATITUDE':None,'LONGITUDE':0}]})==([],1)

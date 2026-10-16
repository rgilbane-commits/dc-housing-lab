import unittest
from unittest.mock import patch
from live_data import fetch_gis, DataUnavailable

class GISCaseTests(unittest.TestCase):
    def test_uppercase_query_and_result(self):
        def fake(url,params,session=None,timeout=9):
            self.assertEqual(params['where'], "PLANNING_AREA = 'ROCK CREEK WEST'")
            return {'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'ROCK CREEK WEST','TOTAL_AFFORDABLE_UNITS':44}}]}
        with patch('live_data.get_json',side_effect=fake):
            result=fetch_gis('Friendship Heights / Ward 3')
        self.assertEqual(result['metrics']['reported_unit_sum'],44)
    def test_other_areas_uppercase(self):
        for neighborhood,expected in [('Columbia Heights / Ward 1','MID-CITY'),('Congress Heights / Ward 8','FAR SOUTHEAST AND SOUTHWEST')]:
            def fake(url,params,session=None,timeout=9):
                self.assertIn(expected,params['where'])
                return {'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':expected,'TOTAL_AFFORDABLE_UNITS':10}}]}
            with patch('live_data.get_json',side_effect=fake):
                self.assertEqual(fetch_gis(neighborhood)['metrics']['project_count'],1)
    def test_unrelated_area_still_rejected(self):
        with patch('live_data.get_json',return_value={'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'CAPITOL HILL'}}]}):
            with self.assertRaises(DataUnavailable): fetch_gis('Friendship Heights / Ward 3')

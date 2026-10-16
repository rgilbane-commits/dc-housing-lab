import unittest
from unittest.mock import patch
from live_data import fetch_gis, DataUnavailable

class GISLiteralTests(unittest.TestCase):
    def test_congress_heights_uses_actual_source_literal(self):
        def reply(url,params,session=None,timeout=9):
            self.assertEqual(params['where'], "PLANNING_AREA = 'FAR SOUTHEAST AND SOUTHWEST'")
            return {'features':[{'attributes':{'OBJECTID':3,'PLANNING_AREA':'FAR SOUTHEAST AND SOUTHWEST','TOTAL_AFFORDABLE_UNITS':81}}]}
        with patch('live_data.get_json',side_effect=reply):
            result=fetch_gis('Congress Heights / Ward 8')
        self.assertEqual(result['metrics']['reported_unit_sum'],81)
        self.assertEqual(result['metrics']['project_count'],1)
    def test_unrelated_geography_is_rejected(self):
        with patch('live_data.get_json',return_value={'features':[{'attributes':{'OBJECTID':3,'PLANNING_AREA':'FAR NORTHEAST AND SOUTHEAST'}}]}):
            with self.assertRaises(DataUnavailable):
                fetch_gis('Congress Heights / Ward 8')

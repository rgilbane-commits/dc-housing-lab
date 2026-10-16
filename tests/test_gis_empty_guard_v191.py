import unittest
from unittest.mock import patch
from live_data import fetch_gis, DataUnavailable

class EmptyGuardTests(unittest.TestCase):
    def test_zero_matching_rows_not_reported_as_verified_zero(self):
        with patch('live_data.get_json',return_value={'features':[{'attributes':{'PLANNING_AREA':'ROCK CREEK WEST NEW LABEL'}}]}):
            with self.assertRaisesRegex(DataUnavailable,'Cannot uniquely match'):
                fetch_gis('Friendship Heights / Ward 3')
    def test_empty_source_not_reported_as_true_zero(self):
        with patch('live_data.get_json',return_value={'features':[]}):
            with self.assertRaisesRegex(DataUnavailable,'No valid planning-area names'):
                fetch_gis('Friendship Heights / Ward 3')
    def test_normal_match_preserved(self):
        def fake(url,params,session=None,timeout=9):
            if params.get('returnDistinctValues')=='true':return {'features':[{'attributes':{'PLANNING_AREA':'Rock Creek West'}}]}
            if params.get('returnCountOnly')=='true':return {'count':1}
            return {'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'Rock Creek West','TOTAL_AFFORDABLE_UNITS':22}}]}
        with patch('live_data.get_json',side_effect=fake):
            result=fetch_gis('Friendship Heights / Ward 3')
            self.assertEqual(result['metrics']['reported_unit_sum'],22)
            self.assertEqual(result['status'],'live_verified')
if __name__=='__main__':unittest.main()

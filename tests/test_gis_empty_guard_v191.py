import unittest
from unittest.mock import patch
from live_data import fetch_gis, DataUnavailable

class EmptyGuardTests(unittest.TestCase):
    def test_zero_matching_rows_not_reported_as_verified_zero(self):
        def fake(url,params,session=None,timeout=9):
            if params['where']=='1=1':
                return {'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'Rock Creek WEST new label'}}]}
            return {'features':[]}
        with patch('live_data.get_json',side_effect=fake):
            with self.assertRaisesRegex(DataUnavailable,'zero is NOT verified'):
                fetch_gis('Friendship Heights / Ward 3')
    def test_empty_source_not_reported_as_true_zero(self):
        with patch('live_data.get_json',return_value={'features':[]}):
            with self.assertRaisesRegex(DataUnavailable,'cannot be verified'):
                fetch_gis('Friendship Heights / Ward 3')
    def test_normal_match_preserved(self):
        with patch('live_data.get_json',return_value={'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'Rock Creek West','TOTAL_AFFORDABLE_UNITS':22}}]}):
            result=fetch_gis('Friendship Heights / Ward 3')
            self.assertEqual(result['metrics']['reported_unit_sum'],22)
            self.assertEqual(result['status'],'live')
if __name__=='__main__':unittest.main()

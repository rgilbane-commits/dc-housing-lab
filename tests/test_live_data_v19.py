import unittest
from unittest.mock import patch
from live_data import (fetch_gis,fetch_acs,summarize_projects,DataUnavailable,CENTERS,
                       parse_census_value)
class LiveDataTests(unittest.TestCase):
    def test_three_neighborhoods(self):self.assertEqual(len(CENTERS),3)
    def test_missing_units_not_zero_imputation(self):
        m=summarize_projects([{'OBJECTID':1,'TOTAL_AFFORDABLE_UNITS':30},{'OBJECTID':2,'TOTAL_AFFORDABLE_UNITS':None}])
        self.assertEqual((m['reported_unit_sum'],m['missing_units_rows']),(30,1))
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(DataUnavailable):summarize_projects([{'OBJECTID':1},{'OBJECTID':1}])
    def test_negative_acs_sentinel(self):self.assertIsNone(parse_census_value('-666666666'))
    def test_without_key(self):
        with self.assertRaises(DataUnavailable):fetch_acs('Columbia Heights / Ward 1','')
    def test_gis_pages_and_fields(self):
        def fake_get(url,params,session=None,timeout=9):
            if params.get('returnDistinctValues')=='true':return {'features':[{'attributes':{'PLANNING_AREA':'MID-CITY'}}]}
            if params.get('returnCountOnly')=='true':return {'count':1}
            self.assertIn('PLANNING_AREA',params['where'])
            return {'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'Mid-City','TOTAL_AFFORDABLE_UNITS':23}}]}
        with patch('live_data.get_json',side_effect=fake_get):g=fetch_gis('Columbia Heights / Ward 1')
        self.assertEqual(g['metrics']['reported_unit_sum'],23)
    def test_gis_wrong_geography_rejected(self):
        with patch('live_data.get_json',return_value={'features':[{'attributes':{'OBJECTID':1,'PLANNING_AREA':'Other'}}]}):
            with self.assertRaises(DataUnavailable):fetch_gis('Columbia Heights / Ward 1')
    def test_gis_network_outage(self):
        with patch('live_data.get_json',side_effect=DataUnavailable('offline')):
            with self.assertRaises(DataUnavailable):fetch_gis('Congress Heights / Ward 8')
    def test_census_geocoder_and_income(self):
        def fake(url,params,session=None,timeout=9):
            if 'geocoder' in url:return {'result':{'geographies':{'Census Tracts':[{'TRACT':'003401'}]}}}
            return [['NAME','B19013_001E','B19013_001M','state','county','tract'],['Sample tract','87000','12000','11','001','003401']]
        with patch('live_data.get_json',side_effect=fake):a=fetch_acs('Friendship Heights / Ward 3','fake-key')
        self.assertEqual(a['median_household_income'],87000)
    def test_census_invalid_response_rejected(self):
        with patch('live_data.get_json',return_value={}):
            with self.assertRaises(DataUnavailable):fetch_acs('Friendship Heights / Ward 3','fake-key')
if __name__=='__main__':unittest.main()

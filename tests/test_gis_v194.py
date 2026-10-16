import unittest
from unittest.mock import patch
from live_data import fetch_gis,DataUnavailable,match_gis_area,normalize_area

AREAS=['FAR SOUTHEAST AND SOUTHWEST','MID-CITY','ROCK CREEK WEST']

def mock_api(rows, expected=None, bad=False):
    expected=len(rows) if expected is None else expected
    def fake(url, params, session=None, timeout=9):
        if params.get('returnDistinctValues')=='true':
            return {'features':[{'attributes':{'PLANNING_AREA':v}} for v in AREAS]}
        if params.get('returnCountOnly')=='true':return {'count':expected}
        offset=params.get('resultOffset',0)
        size=params.get('resultRecordCount',500)
        return {'features':[{'attributes':r} for r in rows[offset:offset+size]]}
    return fake

class GISTests(unittest.TestCase):
    def test_names(self):
        self.assertEqual(normalize_area('Far Southeast & Southwest'),normalize_area('FAR SOUTHEAST AND SOUTHWEST'))
        self.assertEqual(match_gis_area('Far Southeast and Southwest',AREAS),'FAR SOUTHEAST AND SOUTHWEST')
        self.assertEqual(match_gis_area('Mid-City',AREAS),'MID-CITY')
        self.assertEqual(match_gis_area('Rock Creek West',AREAS),'ROCK CREEK WEST')
    def test_unrelated(self):
        with self.assertRaises(DataUnavailable):match_gis_area('Capitol Hill',AREAS)
    def test_multi_page_and_missing(self):
        rows=[{'OBJECTID':i,'PLANNING_AREA':'FAR SOUTHEAST AND SOUTHWEST','TOTAL_AFFORDABLE_UNITS':None if i==3 else 10} for i in range(1,6)]
        with patch('live_data.get_json',side_effect=mock_api(rows)):
            result=fetch_gis('Congress Heights / Ward 8',page_size=2)
        self.assertEqual(result['metrics']['project_count'],5)
        self.assertEqual(result['metrics']['reported_unit_sum'],40)
        self.assertEqual(result['metrics']['missing_units_rows'],1)
    def test_verified_zero(self):
        with patch('live_data.get_json',side_effect=mock_api([])):
            r=fetch_gis('Congress Heights / Ward 8')
        self.assertEqual(r['status'],'verified_zero')
    def test_incomplete(self):
        rows=[{'OBJECTID':1,'PLANNING_AREA':'MID-CITY','TOTAL_AFFORDABLE_UNITS':12}]
        with patch('live_data.get_json',side_effect=mock_api(rows,expected=3)):
            with self.assertRaises(DataUnavailable):fetch_gis('Columbia Heights / Ward 1')
    def test_duplicate(self):
        rows=[{'OBJECTID':1,'PLANNING_AREA':'MID-CITY'},{'OBJECTID':1,'PLANNING_AREA':'MID-CITY'}]
        with patch('live_data.get_json',side_effect=mock_api(rows)):
            with self.assertRaises(DataUnavailable):fetch_gis('Columbia Heights / Ward 1')
    def test_mismatch(self):
        rows=[{'OBJECTID':1,'PLANNING_AREA':'CAPITOL HILL'}]
        with patch('live_data.get_json',side_effect=mock_api(rows)):
            with self.assertRaises(DataUnavailable):fetch_gis('Congress Heights / Ward 8')
    def test_discovery_limit(self):
        with patch('live_data.get_json',return_value={'features':[],'exceededTransferLimit':True}):
            with self.assertRaises(DataUnavailable):fetch_gis('Congress Heights / Ward 8')
if __name__=='__main__':unittest.main()

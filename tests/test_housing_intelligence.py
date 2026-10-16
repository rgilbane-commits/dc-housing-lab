import pytest
from housing_intelligence import classify_project,analyze_area,normalize_units,comparison_rows
from live_data import DataUnavailable

def rec(i,prod=None,pres=None,total=None):
 return {'OBJECTID':i,'AFFORDABLE_UNITS_PRODUCTION':prod,'AFFORDABLE_UNITS_PRESERVED':pres,'TOTAL_AFFORDABLE_UNITS':total}
def payload(records):
 return {'rows':records,'area':'MID-CITY','status':'live_verified','expected_count':len(records),'retrieved_at':'2026-10-16T12:00:00+00:00'}
def test_classification_complete():
 assert classify_project(rec(1,5,0,5))['classification']=='production'
 assert classify_project(rec(1,0,7,7))['classification']=='preservation'
 assert classify_project(rec(1,5,5,10))['classification']=='mixed'
def test_partial_and_inconsistent():
 assert classify_project(rec(1,10,None,10))['classification']=='partial_production'
 assert classify_project(rec(1,9,5,10))['classification']=='inconsistent'
 assert classify_project(rec(1,None,None,10))['classification']=='unclassified'
def test_area_reconciliation():
 a=analyze_area(payload([rec(1,5,0,5),rec(2,0,8,8)]))
 assert (a['production_units_reported'],a['preservation_units_reported'],a['fully_classified'])==(5,8,True)
 with pytest.raises(DataUnavailable):analyze_area({**payload([]),'expected_count':3})
def test_incomplete_not_complete():
 a=analyze_area(payload([rec(1,5,None,5)]));assert not a['fully_classified']
def test_denominators():
 assert normalize_units(100,5000,'ACS planning area aggregate','2024')==20
 for args in [(100,None,'ACS','2024'),(100,0,'ACS','2024'),(100,5000,None,'2024'),(100,5000,'ACS',None),(None,5000,'ACS','2024')]:assert normalize_units(*args) is None
def test_partial_suppressed_in_comparison():
 c=comparison_rows([payload([rec(1,5,None,5)])],{'MID-CITY':{'households':1000,'source':'verified','year':'2024'}})[0]
 assert c['Production per 1,000 households'] is None

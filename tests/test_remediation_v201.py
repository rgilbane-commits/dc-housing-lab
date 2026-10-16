from dataclasses import replace
from model import Inputs,analyze
from forecast import ForecastAssumptions,project
from live_data import clean_count,DataUnavailable,fetch_gis
from unittest.mock import patch
import pytest

def test_public_debt_unsupported_not_feasible():
    r=analyze(replace(Inputs(),loan_m=100))
    assert not r['public_loan_supported'] and not r['financing_feasible'] and r['private_debt_capacity']==0

def test_ordinary_public_debt_supported():
    r=analyze(Inputs())
    assert r['public_loan_supported']

def test_negative_forward_noi_disables_exit():
    p=Inputs();r=analyze(p)
    f=project(p,r,ForecastAssumptions(market_growth_pct=-15,restricted_growth_pct=-15,expense_inflation_pct=15))
    assert f['year_11_noi']<0 and f['sale_price'] is None and f['equity_irr'] is None and f['net_sale_to_equity'] is None

def test_integer_counts_only():
    assert clean_count(2.5) is None and clean_count(-2) is None and clean_count('3')==3

def test_gis_changed_count_rejected():
    from live_data import CENTERS
    payloads=[{'count':1},{'features':[{'attributes':{'OBJECTID':4,'PLANNING_AREA':'ROCK CREEK WEST','TOTAL_AFFORDABLE_UNITS':3}}]},{'count':2}]
    with patch('live_data.discover_gis_areas',return_value=['ROCK CREEK WEST']),patch('live_data.get_json',side_effect=payloads):
        with pytest.raises(DataUnavailable):fetch_gis('Friendship Heights / Ward 3')

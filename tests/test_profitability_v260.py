import pytest
from dataclasses import replace
from model import Inputs, analyze
from profitability_sensitivity import Stress, run_case, matrix, break_even_market_rent

def test_zero_shock_reconciles():
    p=Inputs();a=analyze(p);r=run_case(p,Stress())
    assert r['value']==pytest.approx(a['stabilized_value'])
    assert r['additional_equity']==pytest.approx(a['additional_equity_needed'])
    assert r['net_cost_hurdle_gap']==pytest.approx(a['net_cost_margin_gap'])

def test_cap_stress_changes_value_not_noi():
    p=Inputs();base=run_case(p,Stress());stress=run_case(p,Stress(cap_bps=100))
    assert stress['noi']==base['noi']
    assert stress['value']<base['value']

def test_market_shock_does_not_change_restricted_rent():
    p=Inputs(affordable_pct=100)
    assert run_case(p,Stress(rent_pct=25))['noi']==run_case(p,Stress())['noi']

def test_rate_stress_no_valuation_effect():
    p=Inputs();a=run_case(p,Stress());b=run_case(p,Stress(private_rate_bps=300))
    assert b['value']==a['value']
    assert b['private_debt_capacity']<=a['private_debt_capacity']

def test_cost_stress_monotonic_value_cost_spread():
    p=Inputs();a=run_case(p,Stress());b=run_case(p,Stress(cost_pct=10))
    assert b['value']==a['value']
    assert b['value_spread']<a['value_spread']

def test_loan_not_grant():
    p=Inputs();r=run_case(p,Stress());s=run_case(replace(p,loan_m=10),Stress())
    assert r['value_spread']==s['value_spread']
    assert r['net_cost_hurdle_gap']==s['net_cost_hurdle_gap']

def test_matrix_dimensions():
    a=matrix(Inputs());assert len(a)==7 and all(len(row)==7 for row in a)

def test_break_even_market_rent():
    p=Inputs();rent=break_even_market_rent(p)
    assert rent is not None
    assert run_case(replace(p,market_rent=rent),Stress())['value_spread']==pytest.approx(0,abs=.01)

def test_no_market_units():
    assert break_even_market_rent(Inputs(affordable_pct=100)) is None

def test_invalid_stress():
    with pytest.raises(ValueError):run_case(Inputs(),Stress(cost_pct=-101))
    with pytest.raises(ValueError):run_case(Inputs(),Stress(cap_bps=-1000))

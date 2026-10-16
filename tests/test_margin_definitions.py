from dataclasses import replace
from model import Inputs, analyze

def close(a,b):
    assert abs(a-b)<1e-5

def test_independent_margin_definitions():
    p=Inputs(units=200,cost_per_unit=450000,land_credit_m=0,grant_m=15,return_margin_pct=10)
    r=analyze(p)
    c=r['net_cost'];g=r['grant'];v=r['stabilized_value']
    close(r['legacy_total_cost_margin_gap'],c*1.1-g-v)
    close(r['net_cost_margin_gap'],(c-g)*1.1-v)
    close(r['unsubsidized_value_cost_spread'],v-c)
    close(r['legacy_total_cost_margin_gap']-r['net_cost_margin_gap'],0.1*g)

def test_grant_not_a_loan():
    r=analyze(Inputs(grant_m=10)); loan=analyze(Inputs(grant_m=10,loan_m=15))
    close(r['net_cost_margin_gap'],loan['net_cost_margin_gap'])
    close(r['unsubsidized_value_cost_spread'],loan['unsubsidized_value_cost_spread'])

def test_excess_grants_not_profit_in_net_cost_screen():
    r=analyze(Inputs(grant_m=500))
    assert r['net_capital_cost_after_eligible_grant']==0
    assert r['grant_above_net_cost']>0
    close(r['net_cost_margin_gap'],-r['stabilized_value'])

def test_negative_margin_gap_is_signed():
    r=analyze(Inputs(grant_m=100))
    assert r['legacy_total_cost_margin_gap']<0
    assert r['meets_simple_test']

def test_unsubsidized_spread_grant_invariant():
    a=analyze(Inputs(grant_m=0));b=analyze(Inputs(grant_m=20))
    close(a['unsubsidized_value_cost_spread'],b['unsubsidized_value_cost_spread'])

def test_ui_does_not_hide_surplus():
    from pathlib import Path
    s=(Path(__file__).parents[1]/'app.py').read_text()
    assert "if r['margin_gap']>0 else 'None'" not in s
    assert 'Stabilized value plus the modeled grant' in s

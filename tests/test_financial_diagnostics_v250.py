import pytest
from dataclasses import replace
from model import Inputs, analyze
from financial_diagnostics import diagnostics, chart_data

def test_default_identity_and_bps():
    r=analyze(Inputs());d=diagnostics(r)
    assert d['yield_on_cost_pct']==pytest.approx(r['noi']/r['net_cost']*100)
    assert d['yield_cap_spread_bps']==pytest.approx((r['noi']/r['net_cost']-r['cap_rate_pct']/100)*10000)
    assert d['unsubsidized_value_creation']==pytest.approx(r['stabilized_value']-r['net_cost'])
    assert d['legacy_hurdle_headroom']==pytest.approx(-r['economic_gap'])
    assert d['net_cost_hurdle_headroom']==pytest.approx(-r['net_cost_margin_gap'])

def test_grant_changes_funding_not_value_yield():
    p=Inputs();a=diagnostics(analyze(replace(p,grant_m=0)));b=diagnostics(analyze(replace(p,grant_m=20)))
    for k in ('yield_on_cost_pct','unsubsidized_value_creation','yield_cap_spread_bps'):
        assert a[k]==pytest.approx(b[k])
    assert b['net_cost_hurdle_headroom']-a['net_cost_hurdle_headroom']==pytest.approx(20e6*1.1)

def test_public_loan_is_not_grant():
    a=diagnostics(analyze(Inputs()));b=diagnostics(analyze(replace(Inputs(),loan_m=20)))
    assert a['unsubsidized_value_creation']==b['unsubsidized_value_creation']
    assert a['grant_adjusted_value_headroom']==b['grant_adjusted_value_headroom']

def test_infeasible_public_loan_flagged():
    d=diagnostics(analyze(replace(Inputs(),loan_m=150)))
    assert not d['dscr_supported']
    assert d['dscr_headroom_annual']<0

def test_negative_value_spread_and_cap_spread():
    d=diagnostics(analyze(replace(Inputs(),cost_per_unit=900000)))
    assert not d['economic_value_positive']
    assert not d['unsubsidized_yield_advantage']

def test_charts_reconcile():
    r=analyze(Inputs());d=diagnostics(r);c=chart_data(d)
    assert c['value_bridge'][-1]['Amount ($)']==pytest.approx(r['stabilized_value'])
    assert min(v['Private debt ($)'] for v in c['debt_limits'])==pytest.approx(r['private_debt_capacity'])

def test_reject_inconsistent_value():
    r=analyze(Inputs());r['stabilized_value']+=100
    with pytest.raises(ValueError,match='inconsistent'): diagnostics(r)

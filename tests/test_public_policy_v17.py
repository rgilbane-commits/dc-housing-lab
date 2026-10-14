import pytest
from model import Inputs,analyze
from public_policy import evaluate,loan_pv_support,PublicPolicyAssumptions

def test_zero_principal():assert loan_pv_support(0,3,30,5)==0

def test_par_rate_no_concession():assert abs(loan_pv_support(1e7,5,30,5))<1e-5

def test_below_market_positive():assert loan_pv_support(1e7,1,30,5)>0

def test_above_market_negative():assert loan_pv_support(1e7,8,30,5)<0

def test_zero_discount():assert loan_pv_support(1e6,0,10,0)==0

def test_invalid():
    with pytest.raises(ValueError):loan_pv_support(1e6,3,0,5)

def test_reconciliation():
    p=Inputs(loan_m=10,grant_m=5,land_credit_m=2)
    r=analyze(p); d=evaluate(p,r)
    assert d['net_public_support_pv']==pytest.approx(d['grant']+d['land_contribution_value']+d['loan_pv_concession'])
    assert d['restricted_unit_years']==r['restricted_units']*30
    assert d['support_pv_per_restricted_unit_year']==pytest.approx(d['net_public_support_pv']/d['restricted_unit_years'])

def test_no_affordable_units():
    p=Inputs(affordable_pct=0);d=evaluate(p,analyze(p))
    assert d['support_pv_per_restricted_home'] is None
    assert d['support_pv_per_restricted_unit_year'] is None

def test_longer_restriction_lower_cost_per_year():
    p=Inputs();r=analyze(p)
    first=evaluate(p,r,PublicPolicyAssumptions(15));second=evaluate(p,r,PublicPolicyAssumptions(30))
    assert first['support_pv_per_restricted_unit_year']==pytest.approx(second['support_pv_per_restricted_unit_year']*2)

def test_loan_proceeds_are_not_grants():
    p=Inputs(grant_m=0,loan_m=10,loan_rate_pct=3)
    d=evaluate(p,analyze(p))
    assert d['net_public_support_pv']<d['loan_face']

def test_error_bad_assumptions():
    p=Inputs();r=analyze(p)
    with pytest.raises(ValueError):evaluate(p,r,PublicPolicyAssumptions(0))

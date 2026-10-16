import pytest
from investment_strategy import Line, AREAS
from investment_feasibility import assess_line, assess_portfolio, FundingAssumptions

def line(strategy='Mixed-income',amount=10,support=175000):
    return Line(AREAS[0],strategy,amount,support)

def test_reconcile_allocation():
    x=assess_line(line())
    assert x['grant_used']+x['uncommitted_allocation']==pytest.approx(10e6,abs=.01)
    assert x['delivery_verified'] is False

def test_no_homes_zero():
    r=assess_line(line(amount=0));assert r['total_dscr'] is None and not r['finance_screen_pass']

def test_unsupported_equity():
    r=assess_line(line(),FundingAssumptions(committed_equity_pct_of_cost=0))
    assert r['additional_equity_needed']>=0

def test_increased_equity_reduces_shortfall():
    low=assess_line(line(),FundingAssumptions(committed_equity_pct_of_cost=0))
    high=assess_line(line(),FundingAssumptions(committed_equity_pct_of_cost=90))
    assert high['additional_equity_needed']<=low['additional_equity_needed']

def test_reject_overbudget():
    with pytest.raises(ValueError): assess_portfolio([line(amount=101)])

def test_portfolio_totals():
    p=assess_portfolio([line(),Line(AREAS[1],'Preservation',10,110000)])
    assert p['allocation']['allocated_m']==20
    assert p['delivered_homes']==0
    assert p['screened_homes']<=p['potential_homes']

def test_invalid_controls():
    with pytest.raises(ValueError): assess_line(line(),FundingAssumptions(reserve_pct_of_noi=-1))

def test_large_project_screen_blocked():
    r=assess_line(line(amount=100,support=10000))
    assert r['financial_screen'].startswith('EXCEEDS') and r['equity_required'] is None

def test_different_strategy_cost_and_rent():
    a=assess_line(line('Preservation',10,110000)); b=assess_line(line('Deep affordability',10,425000))
    assert a['project_cost']!=b['project_cost'] and a['restricted_homes']>b['restricted_homes']

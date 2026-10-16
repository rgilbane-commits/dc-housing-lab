from dataclasses import replace
import math
import pytest
from model import Inputs, analyze
from development_returns import DevelopmentAssumptions, calculate


def base():
    p=Inputs(); return p,analyze(p)


def test_ledger_lengths_and_uses():
    p,r=base(); a=DevelopmentAssumptions(construction_months=18,hold_months=60)
    result=calculate(p,r,a)
    assert len(result['rows'])==78
    assert len(result['cash_flows'])==79
    assert sum(x['development_uses'] for x in result['rows'])==pytest.approx(r['net_cost'])
    assert sum(x['grant_draw'] for x in result['rows'])==pytest.approx(r['grant'])
    assert sum(x['construction_debt_draw'] for x in result['rows'])==pytest.approx(result['construction_loan_peak'])
    assert result['rows'][17]['construction_debt_balance']==pytest.approx(result['construction_loan_peak'])
    assert result['ending_private_debt']>=0


def test_construction_sources_uses_identity():
    p,r=base();out=calculate(p,r)
    invested=out['equity_contributed_during_construction']
    assert invested+r['grant']+out['construction_loan_peak']==pytest.approx(r['net_cost']+out['construction_interest']+out['construction_fee'])
    assert out['net_permanent_financing_proceeds']==pytest.approx(r['funded_private_debt']+r['loan']-out['construction_loan_peak']-out['permanent_loan_fee'])
    assert out['sale_value']==pytest.approx(out['terminal_noi']/.06)
    assert out['net_sale_to_equity']==pytest.approx(out['sale_value']*.98-out['ending_private_debt']-out['ending_public_debt'])
    assert sum(out['cash_flows'])==pytest.approx(sum(x['net_equity_cash_flow'] for x in out['rows']))


def test_zero_rate_and_zero_construction_debt():
    p,r=base(); out=calculate(p,r,DevelopmentAssumptions(construction_loan_pct=0,construction_rate_pct=0))
    assert out['construction_interest']==0
    assert out['construction_loan_peak']==0
    assert out['levered_irr'] is not None


def test_higher_exit_cap_lowers_return():
    p,r=base(); lo=calculate(p,r,DevelopmentAssumptions(sale_cap_pct=5.5)); hi=calculate(p,r,DevelopmentAssumptions(sale_cap_pct=7))
    assert lo['sale_value']>hi['sale_value']
    assert lo['levered_irr']>hi['levered_irr']


def test_more_construction_interest_reduces_return():
    p,r=base(); lo=calculate(p,r,DevelopmentAssumptions(construction_rate_pct=4)); hi=calculate(p,r,DevelopmentAssumptions(construction_rate_pct=12))
    assert hi['construction_interest']>lo['construction_interest']
    assert hi['levered_irr']<lo['levered_irr']


def test_unfunded_equity_warning_and_overlarge_public_debt():
    p=replace(Inputs(),committed_equity_m=0)
    r=analyze(p)
    assert 'additional equity' in calculate(p,r)['warning']
    p=replace(Inputs(),loan_m=70)
    with pytest.raises(ValueError,match='public loan'):calculate(p,analyze(p))


def test_invalid_terms_and_excess_construction_funding():
    p,r=base()
    with pytest.raises(ValueError):calculate(p,r,DevelopmentAssumptions(construction_months=0))
    with pytest.raises(ValueError):calculate(p,r,DevelopmentAssumptions(sale_cap_pct=0))
    with pytest.raises(ValueError,match='Construction draws exceed'):calculate(p,r,DevelopmentAssumptions(construction_loan_pct=95))


def test_return_metrics_are_finite_and_ledger_agrees():
    p,r=base();out=calculate(p,r)
    assert math.isfinite(out['levered_irr']) and math.isfinite(out['equity_multiple'])
    assert out['equity_multiple']>0
    assert out['rows'][-1]['net_equity_cash_flow'] == pytest.approx(out['cash_flows'][-1])

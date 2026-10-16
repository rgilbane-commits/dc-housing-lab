from dataclasses import replace
import pytest
from investment_strategy import AREAS,STRATEGIES,Line
from investment_feasibility import FundingAssumptions
from scenario_compare import capture, compare, summarize

def lines(amount=0):
    return [Line(area,strategy,amount if (area,strategy)==(AREAS[0],STRATEGIES[0]) else 0,250000) for area in AREAS for strategy in STRATEGIES]

def test_capture_snapshot_immutable_when_input_list_changes():
    original=lines(10)
    a=capture('A',original,FundingAssumptions())
    original[0]=replace(original[0],allocation_m=20)
    assert summarize(a)['allocated_m']==10

def test_comparison_reconciles_and_is_antisymmetric():
    a=capture('A',lines(10),FundingAssumptions())
    b=capture('B',lines(20),FundingAssumptions())
    result=compare(a,b)
    reverse=compare(b,a)
    assert result['delta']['allocated_m']==10
    assert result['delta']['potential_homes']==40
    assert result['delta']['potential_homes']==-reverse['delta']['potential_homes']
    assert result['baseline']['delivered_homes']==result['candidate']['delivered_homes']==0
    assert sum(result['candidate']['areas'].values())==20
    assert sum(result['candidate']['strategies'].values())==20

def test_infeasible_budget_is_rejected():
    with pytest.raises(ValueError):summarize(capture('Over',lines(105),FundingAssumptions()))

def test_invalid_capture_rejected():
    with pytest.raises(ValueError):capture('',lines(),FundingAssumptions())
    with pytest.raises(ValueError):capture('Missing',lines()[:1],FundingAssumptions())

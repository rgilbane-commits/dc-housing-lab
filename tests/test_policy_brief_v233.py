from io import BytesIO
import pytest
from pypdf import PdfReader
from model import Inputs,analyze
from investment_strategy import Line, AREAS,STRATEGIES
from investment_feasibility import FundingAssumptions
from scenario_compare import capture
from policy_brief import build_project_brief, build_scenario_brief

def test_project_pdf_contains_actual_model_numbers():
    p=Inputs();r=analyze(p)
    data=build_project_brief('Test Area','Base',p,r,as_of='2026-10-16')
    text=PdfReader(BytesIO(data)).pages[0].extract_text()
    assert f"{r['units']:,}" in text
    assert '2026-10-16' in text and 'FINANCING' not in text[:5]
    assert 'not lender' in text

def test_project_report_rejects_incomplete_model_output():
    with pytest.raises(ValueError):build_project_brief('A','B',Inputs(),{'units':4})

def test_snapshot_pdf_reports_no_delivered_homes():
    lines=[Line(a,s,0.0,250000.0) for a in AREAS for s in STRATEGIES]
    a=capture('A',lines,FundingAssumptions())
    other=list(lines);other[0]=Line(AREAS[0],STRATEGIES[0],10.0,250000.0)
    b=capture('B',other,FundingAssumptions())
    t=PdfReader(BytesIO(build_scenario_brief(a,b,as_of='2026-10-16'))).pages[0].extract_text()
    assert 'Verified delivered homes' in t and 'SCENARIO B' in t
    assert '10,000,000' in t

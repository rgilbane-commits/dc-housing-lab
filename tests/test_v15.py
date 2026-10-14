import sys,types
from io import BytesIO
from dataclasses import replace
from pathlib import Path
import pytest
from pypdf import PdfReader
from model import Inputs, analyze, neighborhood_inputs, PRESETS, NEIGHBORHOODS
from student_report import create_student_pdf

sys.modules.setdefault('streamlit_folium',types.SimpleNamespace(st_folium=lambda *args,**kwargs:None))
from neighborhood_map import NEIGHBORHOOD_CENTERS, nearest_neighborhood

@pytest.mark.parametrize('name',list(NEIGHBORHOOD_CENTERS))
def test_map_neighborhood_marker(name):
    lat,lon=NEIGHBORHOOD_CENTERS[name]
    assert nearest_neighborhood({'lat':lat,'lng':lon})==name

def test_map_rejects_wrong_click():
    assert nearest_neighborhood({'lat':0,'lng':0}) is None
    assert nearest_neighborhood(None) is None
    assert nearest_neighborhood({'lat':'abc','lng':0}) is None

@pytest.mark.parametrize('scenario',list(PRESETS))
def test_pdf_one_page_and_reconciles(scenario):
    p=neighborhood_inputs('Friendship Heights / Ward 3',scenario)
    r=analyze(p)
    pdf=create_student_pdf('Team Metro','Friendship Heights / Ward 3','Balanced access',p,r)
    reader=PdfReader(BytesIO(pdf))
    assert len(reader.pages)==1
    text=reader.pages[0].extract_text()
    assert 'STUDENT DEVELOPMENT PROPOSAL' in text
    assert 'Total DSCR' in text
    assert f"{r['units']:,}" in text
    assert f"{r['restricted_units']:,}" in text

@pytest.mark.parametrize('p',[
    Inputs(),replace(Inputs(),loan_m=25,private_debt_m=80),
    replace(Inputs(),affordable_pct=100,affordable_rent=500,grant_m=0,loan_m=50),
    replace(Inputs(),units=500,market_rent=6000,cost_per_unit=800000)
])
def test_pdf_stays_one_page_extremes(p):
    r=analyze(p)
    pdf=create_student_pdf('A'*40,'Congress Heights / Ward 8','Deeper affordability',p,r)
    assert len(PdfReader(BytesIO(pdf)).pages)==1

def test_presentation_and_map_hooks_present():
    app=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
    assert "pending_map_neighborhood" in app
    assert "presentation_mode" in app
    assert "create_student_pdf(" in app
    assert "render_map(place)" in app

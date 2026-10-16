from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'app.py').read_text()

def test_five_workspaces():
    tree=ast.parse(SRC)
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='tabs']
    assert len(calls)==1
    tabs=ast.literal_eval(calls[0].args[0])
    assert len(tabs)==5
    assert all(label in str(tabs) for label in ['Overview','Development Studio','DC Housing Explorer','Investment Strategy','Presentation & Reports'])

def test_ten_legacy_sections_retained():
    import re
    assert sorted(int(x) for x in re.findall(r'^with tabs\[(\d+)\]:',SRC,re.M))==list(range(10))
    assert 'tabs=[workspaces[i] for i in [4,1,2,1,4,1,4,1,3,3]]' in SRC

def test_overview_uses_model_results():
    assert "r=analyze(p)" in SRC
    for key in ['restricted_units','additional_equity_needed','legacy_total_cost_margin_gap','total_dscr','funded_private_debt']:
        assert "r['"+key+"']" in SRC
    assert 'finance_stack(breakdown(r)' in SRC
    assert 'waterfall_chart(annual_waterfall(r)' in SRC

def test_downloads_and_callbacks_preserved():
    for marker in ['Download project feasibility screen','Download capital stack','Download annual cash-flow waterfall','apply_density_bonus','apply_land_contribution','apply_grant','create_student_pdf']:
        assert marker in SRC

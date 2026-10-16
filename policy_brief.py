"""PDF exports of existing model outputs and saved illustrative investment scenarios."""
from io import BytesIO
from datetime import date
from math import isfinite
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from scenario_compare import compare

NAVY=HexColor('#18374b');TEAL=HexColor('#087f7a');GREY=HexColor('#536776')
def _cash(v): return ('-' if v<0 else '')+'${:,.0f}'.format(abs(v))
def _header(c,title,subtitle):
    c.setFillColor(NAVY);c.rect(0,702,612,90,stroke=0,fill=1)
    c.setFillColor(HexColor('#ffffff'));c.setFont('Helvetica-Bold',20);c.drawString(43,750,'DC HOUSING LAB')
    c.setFont('Helvetica',10);c.drawString(43,730,title)
    c.setFillColor(GREY);c.setFont('Helvetica',9);c.drawString(43,681,subtitle[:108])
def _line(c,y,label,value):
    c.setFillColor(GREY);c.setFont('Helvetica',9);c.drawString(44,y,label)
    c.setFillColor(NAVY);c.setFont('Helvetica-Bold',10);c.drawRightString(567,y,str(value))
    c.setStrokeColor(HexColor('#e2e9ed'));c.line(44,y-8,568,y-8)
def _footer(c):
    c.setFillColor(GREY);c.setFont('Helvetica',8)
    c.drawString(44,52,'CLASSROOM MODEL. Illustrative inputs; no entitlement, financing commitment or delivery verification.')
    c.drawString(44,40,'GIS/Census data must be independently checked before policy or investment reliance.')
def build_project_brief(place,scenario,p,r,as_of=None):
    if not isinstance(r,dict) or not {'units','restricted_units','net_cost','noi','grant','equity_required','additional_equity_needed','public_loan_supported'}<=r.keys():
        raise ValueError('Incomplete model output')
    date_label=as_of or date.today().isoformat()
    buf=BytesIO();c=canvas.Canvas(buf,pagesize=letter);c.setTitle('DC Housing Lab - Development Policy Brief')
    _header(c,'DEVELOPMENT POLICY BRIEF',f'{place}  |  {scenario}  |  Generated {date_label}')
    c.setFillColor(TEAL);c.setFont('Helvetica-Bold',12);c.drawString(44,652,'DEVELOPMENT AND AFFORDABILITY')
    for y,label,val in [(623,'Homes',f"{r['units']:,}"),(595,'Income-restricted homes',f"{r['restricted_units']:,}"),(567,'Net development cost',_cash(r['net_cost'])),(539,'Annual stabilized NOI',_cash(r['noi'])),(511,'Public grant',_cash(r['grant'])),(483,'Repayable public loan',_cash(r.get('loan',0))),(455,'Equity required',_cash(r['equity_required'])),(427,'Additional equity needed',_cash(r['additional_equity_needed'])),(399,'Total-cost hurdle after grant',_cash(r.get('economic_gap',0))),(371,'Public loan coverage test','PASS' if r['public_loan_supported'] else 'FAIL')]: _line(c,y,label,val)
    c.setFillColor(TEAL);c.setFont('Helvetica-Bold',12);c.drawString(44,320,'KEY ASSUMPTIONS')
    for y,label,value in [(294,'Affordable share',f'{p.affordable_pct:.0f}%'),(272,'Market rent / month',_cash(p.market_rent)),(250,'Restricted rent / month',_cash(p.affordable_rent)),(228,'Cost per unit',_cash(p.cost_per_unit)),(206,'Capitalization rate',f'{p.cap_rate_pct:.2f}%')]: _line(c,y,label,value)
    c.setFillColor(NAVY);c.setFont('Helvetica',9)
    c.drawString(44,148,'Sensitivity: results change with rents, vacancy, operating costs and subsidy policy.')
    c.drawString(44,132,'The public-loan test and margin test are screens, not lender or agency approvals.')
    _footer(c);c.showPage();c.save();return buf.getvalue()

def build_scenario_brief(snapshot_a,snapshot_b,as_of=None):
    result=compare(snapshot_a,snapshot_b)
    a,b=result['baseline'],result['candidate']
    buf=BytesIO();c=canvas.Canvas(buf,pagesize=letter);c.setTitle('DC Housing Lab - Public Investment Policy Brief')
    _header(c,'PUBLIC INVESTMENT SCENARIO BRIEF',f'{a["name"]} vs {b["name"]} | Generated {as_of or date.today().isoformat()}')
    c.setFillColor(TEAL);c.setFont('Helvetica-Bold',12);c.drawString(44,652,'ALLOCATION AND PROJECT SCREENING')
    c.setFont('Helvetica-Bold',9);c.setFillColor(NAVY);c.drawString(44,627,'MEASURE');c.drawRightString(420,627,'SCENARIO A');c.drawRightString(565,627,'SCENARIO B')
    metrics=[('Allocated public budget',lambda x:_cash(x['allocated_m']*1e6)),('Unallocated budget',lambda x:_cash(x['unallocated_m']*1e6)),('Potential homes (illustrative)',lambda x:str(x['potential_homes'])),('Homes passing financial screen',lambda x:str(x['screened_homes'])),('Additional equity needed',lambda x:_cash(x['equity_shortfall'])),('Verified delivered homes',lambda x:str(x['delivered_homes']))]
    for i,(label,fmt) in enumerate(metrics):
        y=596-35*i;c.setFont('Helvetica',9);c.setFillColor(GREY);c.drawString(44,y,label)
        c.setFillColor(NAVY);c.setFont('Helvetica-Bold',10);c.drawRightString(420,y,fmt(a));c.drawRightString(565,y,fmt(b))
        c.setStrokeColor(HexColor('#e2e9ed'));c.line(44,y-9,568,y-9)
    c.setFillColor(TEAL);c.setFont('Helvetica-Bold',12);c.drawString(44,352,'GEOGRAPHIC ALLOCATION ($M)')
    y=322
    for area in a['areas']:
        c.setFont('Helvetica',9);c.setFillColor(GREY);c.drawString(44,y,area[:44]);c.setFillColor(NAVY);c.drawRightString(420,y,f"{a['areas'][area]:,.1f}");c.drawRightString(565,y,f"{b['areas'][area]:,.1f}");y-=25
    c.setFillColor(TEAL);c.setFont('Helvetica-Bold',12);c.drawString(44,222,'HOUSING STRATEGY ALLOCATION ($M)')
    y=195
    for name in a['strategies']:
        c.setFont('Helvetica',9);c.setFillColor(GREY);c.drawString(44,y,name[:44]);c.setFillColor(NAVY);c.drawRightString(420,y,f"{a['strategies'][name]:,.1f}");c.drawRightString(565,y,f"{b['strategies'][name]:,.1f}");y-=25
    _footer(c);c.showPage();c.save();return buf.getvalue()

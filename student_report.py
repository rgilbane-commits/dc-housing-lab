"""Generate one-page printable student project PDFs using ReportLab."""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter

NAVY=HexColor('#15334b'); TEAL=HexColor('#008f86'); GREY=HexColor('#607489'); LINE=HexColor('#d8e4e9')

def _usd(n):
    return ('-' if n<0 else '') + '${:,.0f}'.format(abs(n))

def create_student_pdf(name, neighborhood, priority, p, r):
    """One page; passed model outputs only, never independently recompute financials."""
    buf=BytesIO(); c=canvas.Canvas(buf,pagesize=letter)
    c.setTitle('DC Housing Lab | Student Development Proposal')
    c.setFillColor(NAVY);c.rect(0,695,612,97,stroke=0,fill=1)
    c.setFillColor(HexColor('#ffffff'));c.setFont('Helvetica-Bold',21)
    c.drawString(44,745,'DC HOUSING LAB')
    c.setFont('Helvetica',10);c.drawString(44,724,'STUDENT DEVELOPMENT PROPOSAL  |  CLASSROOM EDITION v1.5')
    c.setFillColor(NAVY);c.setFont('Helvetica-Bold',13);c.drawString(44,670,('Team: '+(name or 'Unassigned'))[:75])
    c.setFont('Helvetica',10);c.setFillColor(GREY);c.drawString(44,653,neighborhood[:85]);c.drawString(44,636,'Priority: '+priority[:65])
    def section(y,title):
        c.setFillColor(TEAL);c.setFont('Helvetica-Bold',10);c.drawString(44,y,title.upper())
        c.setStrokeColor(LINE);c.line(44,y-8,568,y-8)
    def kv(x,y,label,value):
        c.setFillColor(GREY);c.setFont('Helvetica',9);c.drawString(x,y,label)
        c.setFillColor(NAVY);c.setFont('Helvetica-Bold',12);c.drawString(x,y-19,str(value))
    section(610,'What are we building?')
    kv(44,580,'Total homes',f"{r['units']:,}")
    kv(220,580,'Income-restricted homes',f"{r['restricted_units']:,}")
    kv(410,580,'Restricted share',f"{100*r['restricted_units']/r['units']:.1f}%")
    section(528,'How is the development financed?')
    kv(44,498,'Development uses',_usd(r['net_cost']))
    kv(220,498,'Public grants',_usd(r['grant']))
    kv(410,498,'Repayable public loan',_usd(r['loan']))
    kv(44,448,'Supportable private debt',_usd(r['funded_private_debt']))
    kv(220,448,'Total equity required',_usd(r['equity_required']))
    kv(410,448,'Additional equity needed',_usd(r['additional_equity_needed']))
    section(395,'Can the building sustain operations?')
    kv(44,365,'Annual NOI',_usd(r['noi']))
    kv(220,365,'Total annual debt service',_usd(r['total_annual_debt_service']))
    kv(410,365,'Total DSCR',f"{r['total_dscr']:.2f}x" if r['total_dscr'] is not None else 'No debt')
    cash=r['noi']-r['total_annual_debt_service']
    kv(44,315,'Annual cash flow to equity',_usd(cash))
    kv(220,315,'Total-cost hurdle after grant',_usd(r['margin_gap']))
    coc=cash/r['equity_required']*100 if r['equity_required']>0 else None
    kv(410,315,'Cash-on-cash (illustrative)',f'{coc:.1f}%' if coc is not None else 'N/A')
    section(259,'Defend your decisions')
    c.setFillColor(NAVY);c.setFont('Helvetica',10)
    c.drawString(44,232,'1. Who benefits from your development proposal? Who might be excluded?')
    c.drawString(44,211,'2. What is the most difficult trade-off in your financing or housing mix?')
    c.drawString(44,190,'3. Which public policy change would most improve your proposal?')
    for y in (173,145,117):
        c.setStrokeColor(LINE);c.line(44,y,568,y)
    c.setFont('Helvetica',8);c.setFillColor(GREY)
    c.drawString(44,83,'EDUCATIONAL MODEL: Inputs are illustrative, not official DC rents, zoning, or lender terms.')
    c.drawString(44,70,'Cash flow is before reserves, capital expenditures, income taxes, and distributions.')
    c.drawString(44,57,'A positive economic gap indicates a shortfall; financial outputs are not investment advice.')
    c.showPage();c.save();buf.seek(0);return buf.getvalue()

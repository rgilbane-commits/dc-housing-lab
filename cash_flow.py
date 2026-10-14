"""Annual stabilized operating cash-flow waterfall for education, not a DCF."""
from html import escape
from math import isfinite

CATEGORIES=(('Scheduled rental income','#406b9d'),('Vacancy / collections','#c78155'),('Operating expenses','#bc6170'),('Public debt service','#7f75ba'),('Private debt service','#a17eb0'),('Cash flow to equity','#17877d'))

def annual_waterfall(r):
    """All amounts are annual USD. Debt service never reduces unlevered NOI."""
    gross=float(r['gross_rent']); egi=float(r['egi']); noi=float(r['noi'])
    public=float(r['annual_public_loan_payment']); private=float(r['private_annual_debt_service'])
    eq=float(r['equity_required']); committed=float(r['committed_equity'])
    values=(gross,egi,noi,public,private,eq,committed)
    if not all(isfinite(v) and v>=0 for v in values): raise ValueError('Cash-flow inputs must be finite and nonnegative')
    vacancy=gross-egi; opex=egi-noi
    if vacancy < -0.01 or opex < -0.01: raise ValueError('Revenue reconciliation invalid')
    cash=noi-public-private
    annual=(('Scheduled rental income',gross),('Vacancy / collections',-vacancy),('Operating expenses',-opex),('Net operating income',noi),('Public debt service',-public),('Private debt service',-private),('Cash flow to equity',cash))
    assert abs(gross-vacancy-opex-public-private-cash)<0.01
    return {'rows':annual,'gross':gross,'vacancy':vacancy,'egi':egi,'opex':opex,'noi':noi,
        'public_ds':public,'private_ds':private,'total_ds':public+private,'cash_to_equity':cash,
        'equity_required':eq,'committed_equity':committed,'equity_gap':max(0.0,eq-committed),
        'cash_on_cash_pct':(100*cash/eq if eq>0 else None),
        'total_dscr':(noi/(public+private) if public+private>0 else None),
        'coverage_pass':(public+private==0 or noi/(public+private)>=float(r['min_total_dscr'])-1e-9)}

def waterfall_html(w,formatter):
    """Accessible rows and proportional bars; losses clearly retained as negative."""
    base=max(w['gross'],w['total_ds'],abs(w['cash_to_equity']),1.0)
    lookup=dict(CATEGORIES)
    rows=[]
    for label,value in w['rows']:
        if label=='Net operating income': color='#334b60'
        elif label=='Cash flow to equity' and value<0: color='#c95d5d'
        else: color=lookup.get(label,'#64748b')
        # Absolute magnitude bar, sign remains explicit in label and amount.
        width=min(100.0,100*abs(value)/base)
        rows.append(f'<div style="margin:9px 0"><div style="display:flex;justify-content:space-between;font-size:13px;font-weight:600;gap:12px"><span>{escape(label)}</span><span>{escape(formatter(value))}</span></div><div style="background:#e6edf2;border-radius:5px;height:13px;margin-top:4px"><div style="width:{width:.5f}%;background:{color};height:13px;border-radius:5px"></div></div></div>')
    return '<div style="background:#f4f7fa;border:1px solid #dbe4ec;border-radius:12px;padding:17px;color:#152d40">'+''.join(rows)+'</div>'

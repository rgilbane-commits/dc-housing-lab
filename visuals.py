"""Pure presentation helpers for DC Housing Lab v1.4. Never re-underwrites results."""
from html import escape
from math import ceil, isfinite

CSS = """<style>
:root{--ink:#12263b;--teal:#0c8c89;--muted:#62788a}
.block-container{max-width:1440px;padding-top:1.35rem;padding-bottom:3rem}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#f7fafc 0%,#fff 300px)}
[data-testid="stSidebar"]{background:#f0f5f8}
[data-testid="stMetric"]{background:#fff;border:1px solid #e3eaf0;box-shadow:0 3px 14px rgba(20,44,65,.045);border-radius:14px;padding:14px 18px;min-width:0}
[data-testid="stMetricLabel"]{color:#496577}
[data-testid="stMetricValue"]{color:#132e41;font-weight:730;letter-spacing:-.025em;font-size:clamp(1.15rem,2.2vw,1.9rem)}
h1,h2,h3{color:#142d40;letter-spacing:-.025em}
.hero-v14{color:white;background:linear-gradient(115deg,#14283f 0%,#13556a 63%,#0b8684 100%);border-radius:18px;padding:24px 30px;margin-bottom:14px;box-shadow:0 10px 28px rgba(15,45,66,.12)}
.hero-v14 h1{color:white;margin:0;font-size:clamp(1.65rem,3.2vw,2.55rem);line-height:1.2}.hero-v14 p{color:#d6e7eb;margin:8px 0 0}
.eyebrow{font-size:.73rem;letter-spacing:.13em;font-weight:700;color:#9ee4df;margin-bottom:7px}
.lab-card{background:white;border:1px solid #dfe8ed;border-radius:16px;padding:20px;margin:15px 0;box-shadow:0 4px 15px rgba(15,45,66,.05)}
.lab-title{font-size:1.03rem;font-weight:750;color:#17354a;margin-bottom:7px}.lab-note{color:#516878;font-size:.84rem;line-height:1.6}
.mass-layout{display:grid;grid-template-columns:minmax(180px,1fr) minmax(180px,1fr);gap:20px;align-items:end}
.sky{background:linear-gradient(#e9f5fa,#fbfcfa);border-radius:12px;min-height:190px;padding:15px 14px 0;display:flex;align-items:end;justify-content:center;overflow:hidden}
.massing{width:min(100%,340px);border:4px solid #314e63;border-bottom:7px solid #314e63;border-radius:5px 5px 0 0;background:#e1eaf0;padding:7px;box-shadow:10px 0 0 #b6cbd4}
.mass-floor{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;margin-bottom:3px}.mass-unit{height:13px;border-radius:1px;background:#9fb5c8}.mass-unit.aff{background:#13a39c}.mass-unit.mkt{background:#7191aa}.mass-unit.empty{background:transparent}
.legend-item{display:inline-flex;align-items:center;gap:7px;margin:5px 13px 4px 0;font-size:.85rem;color:#38566a}.legend-swatch{width:12px;height:12px;border-radius:3px;display:inline-block}
.stat-pill{font-weight:700;color:#153a52;font-size:1.04rem;margin-bottom:7px}
.money-row{display:flex;justify-content:space-between;gap:12px;color:#314d60;font-size:.85rem;padding-top:10px}
.stacked-track{display:flex;overflow:hidden;border-radius:9px;height:28px;background:#e8eef2;margin-top:7px}
.stacked-part{height:100%;min-width:0}
.wf-wrap{overflow-x:auto;margin-top:10px}.wf-chart{min-width:620px;width:100%;height:auto;display:block}
@media(max-width:750px){.hero-v14{padding:20px}.mass-layout{grid-template-columns:1fr}.lab-card{padding:15px}.sky{min-height:155px}}
</style>"""
PALETTE=(('#11998e','Public grant'),('#487fb2','Public debt'),('#7762a4','Private debt'),('#d2a041','Committed equity'),('#cb6670','Additional equity'))

def building_massing(units,restricted,units_per_floor=20):
    if not all(isinstance(v,int) for v in (units,restricted,units_per_floor)) or units<1 or not 0<=restricted<=units or units_per_floor<1: raise ValueError('invalid building program')
    floors=ceil(units/units_per_floor)
    # 10 markers per row is a sampled facade, not a unit-by-unit representation.
    rows=[]
    for f in range(min(floors,18)-1,-1,-1):
        cells=[]
        for col in range(10):
            index=f*units_per_floor+int((col+.5)*units_per_floor/10)
            if index>=units: kind='empty'
            else: kind='aff' if index*restricted//units > (index-1)*restricted//units else 'mkt'
            cells.append(f'<span class="mass-unit {kind}"></span>')
        rows.append('<div class="mass-floor">'+''.join(cells)+'</div>')
    if floors>18: rows.insert(0,'<div style="text-align:center;font-size:12px;color:#33566e">+ higher floors not shown</div>')
    share=restricted/units*100
    return (f'<section class="lab-card"><div class="lab-title">What are we building?</div><div class="mass-layout"><div class="sky"><div class="massing" aria-label="Conceptual building massing">'+''.join(rows)+'</div></div>'
        f'<div><div class="stat-pill">{units:,} apartments · {floors:,} conceptual floors</div><div class="lab-note">Assumes {units_per_floor} units per floor for visualization only. Not a zoning, engineering, or design assessment.</div>'
        f'<div class="stacked-track" aria-label="Affordable share {share:.1f} percent"><div class="stacked-part" style="background:#13a39c;width:{share:.5f}%"></div><div class="stacked-part" style="background:#7191aa;flex:1"></div></div>'
        f'<div><span class="legend-item"><span class="legend-swatch" style="background:#13a39c"></span>Restricted {restricted:,} ({share:.1f}%)</span><span class="legend-item"><span class="legend-swatch" style="background:#7191aa"></span>Market-rate {units-restricted:,}</span></div>'
        '</div></div></section>')

def finance_stack(stack, money):
    cost=float(stack['cost'])
    if not isfinite(cost) or cost<0: raise ValueError('invalid uses')
    allocated=dict(stack['allocated'])
    entries=[]
    for name,value in stack['sources']:
        amount=max(0.0,float(allocated.get(name,0)))
        entries.append((str(name),amount))
    entries.append(('Additional equity',max(0.0,float(stack['shortfall']))))
    if abs(sum(v for _,v in entries)-cost)>max(.02,1e-9*max(cost,1)):raise ValueError('capital stack does not reconcile')
    colors=['#11998e','#487fb2','#7762a4','#d2a041','#cb6670']
    # The order follows sources; colors are indexed, not tied to accounting meaning.
    colors=(colors+['#71849b']*len(entries))[:len(entries)]
    segments=''.join(f'<div class="stacked-part" title="{escape(name)}: {escape(money(value))}" style="background:{color};width:{(100*value/cost if cost else 0):.6f}%"></div>' for (name,value),color in zip(entries,colors))
    legend=''.join(f'<span class="legend-item"><span class="legend-swatch" style="background:{color}"></span>{escape(name)}: <b>{escape(money(value))}</b></span>' for (name,value),color in zip(entries,colors) if value>0)
    return f'<section class="lab-card"><div class="lab-title">Sources & uses</div><div class="money-row"><b>Development cost</b><b>{escape(money(cost))}</b></div><div class="stacked-track" style="background:#334b60"></div><div class="money-row"><b>Allocated financing + remaining equity</b><b>{escape(money(cost))}</b></div><div class="stacked-track">{segments}</div><div style="margin-top:12px">{legend}</div><div class="lab-note">Bars reconcile to net development cost. Unused funding offers are excluded from the funded bar, not treated as profit.</div></section>'

def waterfall_chart(w,money):
    # True floating waterfall: change bars begin at prior running cash balance.
    rows=[('Scheduled rent',w['gross'],0,w['gross'],'total'),('Vacancy',-w['vacancy'],w['egi'],w['gross'],'change'),('Operating costs',-w['opex'],w['noi'],w['egi'],'change'),('NOI',w['noi'],0,w['noi'],'total'),('Public debt',-w['public_ds'],w['noi']-w['public_ds'],w['noi'],'change'),('Private debt',-w['private_ds'],w['cash_to_equity'],w['noi']-w['public_ds'],'change'),('Cash to equity',w['cash_to_equity'],0,w['cash_to_equity'],'total')]
    lo=min(0,min(min(a,b) for _,_,a,b,_ in rows));hi=max(1,max(max(a,b) for _,_,a,b,_ in rows));span=hi-lo
    W=980;H=320;left=36;right=18;top=28;bottom=82;chart=H-top-bottom
    def y(v):return top+(hi-v)/span*chart
    parts=[f'<svg class="wf-chart" viewBox="0 0 {W} {H}" role="img" aria-label="Operating waterfall from rent to cash flow to equity"><line x1="{left}" y1="{y(0):.1f}" x2="{W-right}" y2="{y(0):.1f}" stroke="#a1b4c0" stroke-width="1.5"/>']
    step=(W-left-right)/len(rows);bar=step*.61
    for i,(label,value,a,b,kind) in enumerate(rows):
        x=left+i*step+step*.195;ya=min(y(a),y(b));height=max(2,abs(y(a)-y(b)))
        color=('#147f89' if label=='Cash to equity' and value>=0 else '#c75d67' if label=='Cash to equity' else '#315778' if kind=='total' else '#d18a5b' if label in ('Vacancy','Operating costs') else '#7969ae')
        parts.append(f'<rect x="{x:.1f}" y="{ya:.1f}" width="{bar:.1f}" height="{height:.1f}" rx="3" fill="{color}"/>')
        ty=max(15,ya-7) if value>=0 else min(H-bottom+18,ya+height+15)
        parts.append(f'<text x="{x+bar/2:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="12" font-weight="650" fill="#263f50">{escape(money(value))}</text>')
        pieces=label.split(' ');parts.append(f'<text x="{x+bar/2:.1f}" y="{H-57}" text-anchor="middle" font-size="12" fill="#38546a">'+''.join(f'<tspan x="{x+bar/2:.1f}" dy="{0 if j==0 else 15}">{escape(word)}</tspan>' for j,word in enumerate(pieces))+'</text>')
    parts.append('</svg>')
    return '<section class="lab-card"><div class="lab-title">Where does the annual rent go?</div><div class="wf-wrap">'+''.join(parts)+'</div><div class="lab-note">Floating bars subtract expenses and debt payments from running cash. NOI is before debt; ending cash can be negative. One stabilized year only.</div></section>'

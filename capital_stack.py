"""Pure model / presentation helpers for a classroom sources-and-uses diagram."""
from html import escape

COLORS={"Cash grant":"#168a83","Public loan":"#5574a6","Private loan":"#a07cb3","Committed equity":"#d9a352","Additional equity needed":"#c95d5d","Development cost":"#334b60"}

def breakdown(r):
    """Build a reconciled financing view using debt *actually supportable*, not requested debt.
    Overfinancing is explicitly shown as surplus, not mistaken for equity.
    """
    cost=float(r['net_cost'])
    candidates=[('Cash grant',float(r['grant'])),('Public loan',float(r['loan'])),
                ('Private loan',float(r['funded_private_debt'])),
                ('Committed equity',float(r['committed_equity']))]
    if cost < 0 or any(v < 0 for _,v in candidates): raise ValueError('Negative sources/uses')
    source_total=sum(v for _,v in candidates)
    remaining=cost
    allocated=[]
    for label, value in candidates:
        used=min(value,remaining)
        allocated.append((label,used))
        remaining-=used
    allocated.append(('Additional equity needed',remaining))
    unused=sum(v for _,v in candidates)-sum(v for _,v in allocated[:-1])
    assert abs(sum(v for _,v in allocated)-cost)<0.01
    return {'cost':cost,'sources':candidates,'available_total':source_total,
            'allocated':allocated,'shortfall':remaining,'unused_sources':unused,
            'net_gap':cost-source_total}

def visual(r,fmt):
    d=breakdown(r)
    scale=max(d['cost'],d['available_total'],1)
    def bar(items):
        spans=[]
        for label,v in items:
            if v <= 1e-8: continue
            fraction=max(0,v/scale*100)
            tooltip=escape(f'{label}: {fmt(v)}',quote=True)
            spans.append(f'<span title="{tooltip}" style="display:block;width:{fraction:.7f}%;height:34px;background:{COLORS[label]};"></span>')
        return '<div style="display:flex;width:100%;background:#e8edf2;border-radius:7px;overflow:hidden;min-height:34px">'+''.join(spans)+'</div>'
    used=[(label,value) for label,value in d['allocated'] if value]
    costbar=bar([('Development cost',d['cost'])])
    # The second bar represents FULL available committed sources, and explicitly reserves gap if underfunded.
    funded=bar(d['sources'] + ([('Additional equity needed',d['shortfall'])] if d['shortfall']>0 else []))
    legend=''.join(f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:12px"><i style="width:11px;height:11px;background:{COLORS[k]};display:inline-block;border-radius:2px"></i>{escape(k)}</span>' for k,v in d['allocated'] if v>0)
    return f"""<div style="background:#f4f7fa;color:#152d40;padding:16px;border-radius:12px;border:1px solid #dbe4ec">
<div style="font-size:13px;font-weight:700;margin-bottom:6px">NET DEVELOPMENT COST — {fmt(d['cost'])}</div>{costbar}
<div style="font-size:13px;font-weight:700;margin:13px 0 6px">AVAILABLE SOURCES + UNFUNDED EQUITY — {fmt(max(d['cost'],d['available_total']))}</div>{funded}
<div style="margin-top:12px;line-height:26px">{legend}</div>
</div>"""

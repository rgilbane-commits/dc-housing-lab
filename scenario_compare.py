"""Pure comparison of illustrative public investment scenario snapshots."""
from dataclasses import dataclass
from math import isfinite
from investment_strategy import Line, AREAS, STRATEGIES
from investment_feasibility import FundingAssumptions, assess_portfolio

@dataclass(frozen=True)
class Snapshot:
    name: str
    lines: tuple
    funding: FundingAssumptions

def capture(name, lines, controls):
    if not name or not name.strip(): raise ValueError('Scenario name required')
    if len(lines) != len(AREAS)*len(STRATEGIES): raise ValueError('Capture must include all area/strategy allocations')
    if len({(x.area,x.strategy) for x in lines}) != len(lines): raise ValueError('Duplicate allocation')
    return Snapshot(name.strip(),tuple(lines),controls)

def summarize(snapshot):
    if not isinstance(snapshot,Snapshot): raise TypeError('Snapshot required')
    portfolio=assess_portfolio(snapshot.lines,snapshot.funding)
    allocation=portfolio['allocation']
    area_totals={a:0. for a in AREAS}
    strategy_totals={s:0. for s in STRATEGIES}
    for entry in allocation['lines']:
        area_totals[entry['planning_area']]+=entry['allocation_m']
        strategy_totals[entry['strategy']]+=entry['allocation_m']
    return {'name':snapshot.name,'allocated_m':allocation['allocated_m'],
            'unallocated_m':allocation['unallocated_m'],
            'potential_homes':portfolio['potential_homes'],
            'screened_homes':portfolio['screened_homes'],
            'equity_shortfall':portfolio['total_equity_shortfall'],
            'delivered_homes':0,'areas':area_totals,'strategies':strategy_totals,
            'project_rows':tuple(portfolio['projects'])}

def compare(a,b):
    x,y=summarize(a),summarize(b)
    fields=('allocated_m','unallocated_m','potential_homes','screened_homes','equity_shortfall','delivered_homes')
    return {'baseline':x,'candidate':y,'delta':{k:y[k]-x[k] for k in fields},
            'warning':'Illustrative scenario comparison; neither screen pass nor capacity is a committed or delivered home. Differences are model-generated, not causal estimates.'}

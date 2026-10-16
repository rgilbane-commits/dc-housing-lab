"""Pure, recomputed scenario diagnostics. All magnitudes from model.analyze.
These are stabilized educational pro formas, not investment-level IRRs.
"""
from dataclasses import dataclass, replace
from math import isfinite
from model import Inputs, analyze

@dataclass(frozen=True)
class Stress:
    cost_pct: float = 0
    rent_pct: float = 0
    cap_bps: int = 0
    private_rate_bps: int = 0

def run_case(p: Inputs, s: Stress):
    if not all(isfinite(float(v)) for v in (s.cost_pct,s.rent_pct,s.cap_bps,s.private_rate_bps)):
        raise ValueError('Nonfinite shock')
    if s.cost_pct <= -100 or s.rent_pct <= -100:
        raise ValueError('Cost or rent factor must be positive')
    cap = p.cap_rate_pct+s.cap_bps/100
    rate = p.private_rate_pct+s.private_rate_bps/100
    if cap<=0 or rate<0:
        raise ValueError('Invalid stressed cap rate or financing interest')
    stressed = replace(p,
        cost_per_unit=p.cost_per_unit*(1+s.cost_pct/100),
        market_rent=p.market_rent*(1+s.rent_pct/100),
        affordable_rent=p.affordable_rent, # regulated rent unchanged
        cap_rate_pct=cap, private_rate_pct=rate)
    r=analyze(stressed)
    return {'stress':s,'noi':r['noi'],'value':r['stabilized_value'],
            'net_cost':r['net_cost'],'value_spread':r['unsubsidized_value_cost_spread'],
            'net_cost_hurdle_gap':r['net_cost_margin_gap'],
            'legacy_hurdle_gap':r['legacy_total_cost_margin_gap'],
            'private_debt_capacity':r['private_debt_capacity'],
            'equity_required':r['equity_required'],
            'additional_equity':r['additional_equity_needed'],
            'total_dscr':r['total_dscr'],
            'dscr_supported':r['public_loan_supported'] and (r['total_dscr'] is None or r['total_dscr']+1e-9>=p.min_total_dscr),
            'financing_feasible':r['financing_feasible'],
            'economic_hurdle_met':r['net_cost_margin_gap']<=0,
            'screen_pass':r['net_cost_margin_gap']<=0 and r['financing_feasible']}

def matrix(p: Inputs, cost_moves=(-15,-10,-5,0,5,10,15), rent_moves=(-15,-10,-5,0,5,10,15), *, cap_bps=0, private_rate_bps=0):
    return [[run_case(p, Stress(c,r,cap_bps,private_rate_bps)) for r in rent_moves] for c in cost_moves]

def break_even_market_rent(p: Inputs, target='value_cost', lo=0., hi=100000., tol=1e-6):
    """Required monthly market rent (fixed affordable rent), null if no market units or unreachable.
    Economic target only: does not imply funding or operating feasibility.
    """
    if round(p.units*p.affordable_pct/100) >= p.units:
        return None
    def gap(v):
        r=analyze(replace(p,market_rent=v))
        return (r['stabilized_value']-r['net_cost']) if target=='value_cost' else -r['net_cost_margin_gap']
    if target not in ('value_cost','net_cost_hurdle'):
        raise ValueError('Unsupported hurdle')
    if gap(lo)>=0: return 0.
    if gap(hi)<0: return None
    for _ in range(80):
        mid=(lo+hi)/2
        if gap(mid)>=0:hi=mid
        else:lo=mid
    return hi

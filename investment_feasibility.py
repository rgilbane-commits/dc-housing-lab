"""Separate illustrative project-level feasibility tests for allocation candidates.
Never interprets capacity as projects that are approved, delivered or committed.
"""
from dataclasses import dataclass, replace
from math import isfinite
from model import Inputs, NEIGHBORHOODS, analyze
from investment_strategy import STRATEGIES, AREAS, evaluate

AREA_NEIGHBORHOOD = dict(zip(AREAS, NEIGHBORHOODS.keys()))
# Classroom underwriting archetypes only. Preservation cost includes assumed acquisition and rehab.
ARCHETYPES = {
    'New construction': {'cost_multiplier': 1.0, 'restricted_share': 1.0, 'restricted_rent': 1500},
    'Preservation': {'cost_multiplier': 0.62, 'restricted_share': 1.0, 'restricted_rent': 1500},
    'Deep affordability': {'cost_multiplier': 1.06, 'restricted_share': 1.0, 'restricted_rent': 850},
    'Mixed-income': {'cost_multiplier': 1.0, 'restricted_share': 0.4, 'restricted_rent': 1500},
}

@dataclass(frozen=True)
class FundingAssumptions:
    private_debt_request_pct_of_cost: float = 55.0
    committed_equity_pct_of_cost: float = 20.0
    reserve_pct_of_noi: float = 5.0
    require_dscr: float = 1.25

def assess_line(line, controls=FundingAssumptions()):
    if line.area not in AREAS or line.strategy not in STRATEGIES:
        raise ValueError('Unknown planning area or strategy')
    if any(not isfinite(x) for x in (controls.private_debt_request_pct_of_cost,controls.committed_equity_pct_of_cost,controls.reserve_pct_of_noi,controls.require_dscr)):
        raise ValueError('Nonfinite underwriting assumptions')
    if not (0 <= controls.private_debt_request_pct_of_cost <= 100 and 0 <= controls.committed_equity_pct_of_cost <= 100 and 0 <= controls.reserve_pct_of_noi < 100 and controls.require_dscr >= 1):
        raise ValueError('Invalid underwriting assumptions')
    allocation = evaluate([line], budget_m=max(100.0,line.allocation_m))['lines'][0]
    units = allocation['illustrative_home_capacity']
    if units == 0:
        return {'planning_area':line.area,'strategy':line.strategy,'allocation_m':line.allocation_m,'potential_homes':0,'restricted_homes':0,'grant_used':0.0,'uncommitted_allocation':line.allocation_m*1e6,'project_cost':0.0,'noi':None,'noi_after_reserve':None,'total_dscr':None,'equity_required':None,'committed_equity':0.0,'additional_equity_needed':None,'unmet_capital':None,'financial_screen':'NO PROJECT SIZED','finance_screen_pass':False,'economic_screen_pass':False,'operating_screen_pass':False,'delivery_verified':False}
    if units > 2000:
        return {'planning_area':line.area,'strategy':line.strategy,'allocation_m':line.allocation_m,'potential_homes':units,'restricted_homes':None,'grant_used':units*line.support_per_home,'uncommitted_allocation':allocation['unassigned_fractional_budget'],'project_cost':None,'noi':None,'noi_after_reserve':None,'total_dscr':None,'equity_required':None,'committed_equity':None,'additional_equity_needed':None,'unmet_capital':None,'financial_screen':'EXCEEDS 2,000-UNIT PROJECT MODEL LIMIT','finance_screen_pass':False,'economic_screen_pass':False,'operating_screen_pass':False,'delivery_verified':False}
    ar=ARCHETYPES[line.strategy]; neighborhood=NEIGHBORHOODS[AREA_NEIGHBORHOOD[line.area]]
    unit_cost=round(neighborhood['cost_per_unit']*ar['cost_multiplier'])
    grant_used=units*line.support_per_home
    cost=units*unit_cost
    p=Inputs(units=units, affordable_pct=round(ar['restricted_share']*100),market_rent=neighborhood['market_rent'], affordable_rent=ar['restricted_rent'],cost_per_unit=unit_cost,grant_m=grant_used/1e6,loan_m=0,private_debt_m=cost*controls.private_debt_request_pct_of_cost/100/1e6,committed_equity_m=cost*controls.committed_equity_pct_of_cost/100/1e6,min_total_dscr=controls.require_dscr)
    a=analyze(p)
    reserve=a['noi']*controls.reserve_pct_of_noi/100
    cash_after_reserve=a['noi']-reserve
    coverage=cash_after_reserve/a['total_annual_debt_service'] if a['total_annual_debt_service']>0 else None
    ops_ok=cash_after_reserve>=0 and (coverage is None or coverage>=controls.require_dscr-1e-9)
    capital_ok=a['additional_equity_needed']<=0.01 and a['excess_financing_sources']<=0.01
    economic_ok=a['economic_gap']<=0.01
    # This is a SCREEN, never approval. Controls only capture generic, fictional project economics.
    screening_pass=capital_ok and ops_ok and economic_ok
    return {'planning_area':line.area,'strategy':line.strategy,'allocation_m':line.allocation_m,'potential_homes':units,'restricted_homes':a['restricted_units'],'grant_used':grant_used,'uncommitted_allocation':allocation['unassigned_fractional_budget'],'project_cost':a['net_cost'],'noi':a['noi'],'noi_after_reserve':cash_after_reserve,'total_dscr':coverage,'equity_required':a['equity_required'],'committed_equity':a['committed_equity'],'additional_equity_needed':a['additional_equity_needed'],'unmet_capital':a['additional_equity_needed'],'financial_screen':'PASSES ILLUSTRATIVE SCREEN - NOT APPROVED' if screening_pass else 'FAILS ILLUSTRATIVE SCREEN','finance_screen_pass':capital_ok,'economic_screen_pass':economic_ok,'operating_screen_pass':ops_ok,'delivery_verified':False}

def assess_portfolio(lines, controls=FundingAssumptions(), budget_m=100.0):
    base=evaluate(lines,budget_m)
    result=[assess_line(l,controls) for l in lines if l.allocation_m>0]
    return {'allocation':base,'projects':result,'screened_homes':sum(int(v['potential_homes']) for v in result if v['finance_screen_pass'] and v['economic_screen_pass'] and v['operating_screen_pass']),'potential_homes':base['potential_capacity'],'delivered_homes':0,'total_equity_shortfall':sum(v['additional_equity_needed'] or 0 for v in result),'warning':'Screening passes are hypothetical and do not establish a real development opportunity, entitlement, debt commitment, grant award, or completed housing.'}

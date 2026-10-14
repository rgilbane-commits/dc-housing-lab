"""Pure, auditable classroom visualization and interpretive functions. No live data."""
from dataclasses import dataclass
from html import escape
from model import Inputs, analyze

@dataclass(frozen=True)
class Household:
    name: str
    story: str
    annual_income: int
    size: int

HOUSEHOLDS = (
    Household('Public school teacher', 'Illustrative single adult household', 73000, 1),
    Household('Restaurant worker', 'Illustrative single adult household', 38000, 1),
    Household('Healthcare worker with child', 'Illustrative two-person household', 92000, 2),
    Household('Senior on fixed income', 'Illustrative single adult household', 28000, 1),
)

def household_results(p: Inputs, households=HOUSEHOLDS, utility_allowance=150):
    """30% gross-income budget, with utilities separately deducted; no HUD eligibility implied."""
    if utility_allowance < 0: raise ValueError('Utility allowance cannot be negative')
    out=[]
    for h in households:
        if h.annual_income < 0 or h.size < 1: raise ValueError('Invalid household')
        monthly_total=h.annual_income*.3/12
        max_rent=max(0,monthly_total-utility_allowance)
        out.append({'Household':h.name,'Illustrative income ($)':h.annual_income,
                    'Household size':h.size,'30% housing budget ($/mo)':round(monthly_total),
                    'Rent budget after utilities ($/mo)':round(max_rent),
                    'Can afford restricted rent?': 'Yes' if p.affordable_rent <= max_rent else 'No',
                    'Can afford market rent?': 'Yes' if p.market_rent <= max_rent else 'No',
                    'Story':h.story})
    return out

def building_html(units, restricted, columns=10):
    """Stylized housing mix, not a representation of actual massing or zoning."""
    if not 1 <= units <= 2000 or not 0 <= restricted <= units: raise ValueError('Invalid building mix')
    # Cap displayed cells to protect mobile rendering. Each cell represents a share, not one apartment.
    cells=min(units,100)
    assigned=round(cells*restricted/units)
    tiles=''.join('<span class="apt '+('aff' if i < assigned else 'mkt')+'" aria-label="'+('Restricted' if i < assigned else 'Market-rate')+'"></span>' for i in range(cells))
    floors=(units+columns-1)//columns
    return f'''<div role="img" aria-label="Stylized housing mix: {restricted} restricted of {units} apartments; not to scale" class="building"><div class="legend"><span>■ Restricted ({restricted})</span><span>■ Market-rate ({units-restricted})</span></div><div class="windows">{tiles}</div><div class="caption">{units} homes • approximately {floors} hypothetical rows at {columns} units per row • visualization not to scale; maximum 100 tiles</div></div>'''

def tradeoff_messages(p: Inputs, baseline: Inputs):
    """Only report mathematical effects verified from model, with conditional caveats."""
    current=analyze(p); base=analyze(baseline)
    result=[]
    delta_homes=current['restricted_units']-base['restricted_units']
    delta_total=p.units-baseline.units
    delta_noi=current['noi']-base['noi']
    delta_gap=current['margin_gap']-base['margin_gap']
    if delta_total:
        result.append(f"Housing supply: {delta_total:+,} total homes; development cost changes by ${current['gross_cost']-base['gross_cost']:,.0f}. The model assumes every added unit is permitted and buildable.")
    if delta_homes:
        result.append(f"Restricted housing: {delta_homes:+,} homes compared with the loaded baseline. A higher count does not necessarily mean deeper affordability.")
    if abs(delta_noi)>1:
        result.append(f"Annual operating income: {'rises' if delta_noi>0 else 'falls'} by ${abs(delta_noi):,.0f} compared with the baseline.")
    if abs(delta_gap)>1:
        result.append(f"Gap to the classroom required margin: {'worsens' if delta_gap>0 else 'improves'} by ${abs(delta_gap):,.0f} compared with the baseline.")
    if p.grant_m != baseline.grant_m:
        result.append(f"Cash grants changed by ${(p.grant_m-baseline.grant_m)*1e6:+,.0f}; these are nonrepayable public funds in this exercise.")
    if p.loan_m != baseline.loan_m:
        result.append(f"Repayable public loan changed by ${(p.loan_m-baseline.loan_m)*1e6:+,.0f}; proceeds reduce the capital funding gap, not the unlevered economic margin gap. Public-loan debt service affects the public-only DSCR; total-debt DSCR is not modeled.")
    if p.land_credit_m != baseline.land_credit_m:
        result.append('Public land support lowers modeled cost but uses a public asset; this exercise does not price its opportunity cost independently.')
    if not result: result=['You are viewing the loaded baseline. Try increasing affordability, density, or a policy subsidy to see the consequences.']
    if current['residual_noi']<=0:
        result.append('WARNING: annual public-loan payments exceed modeled NOI; the modeled loan cannot be serviced from current operations.')
    if current['restricted_units']==0:
        result.append('This plan does not produce any income-restricted homes, even if total housing production is high.')
    return result

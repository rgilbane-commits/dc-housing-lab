"""DC Housing Lab v1.1: deliberately simplified classroom underwriting; no live market data."""
from dataclasses import dataclass, asdict, replace

@dataclass(frozen=True)
class Inputs:
    units: int = 200
    affordable_pct: int = 30
    market_rent: int = 3000
    affordable_rent: int = 1500
    cost_per_unit: int = 450000
    vacancy_pct: float = 7.0
    opex_pct: float = 40.0
    cap_rate_pct: float = 5.5
    grant_m: float = 15.0
    land_credit_m: float = 0.0
    loan_m: float = 0.0
    loan_rate_pct: float = 3.0
    loan_years: int = 30
    return_margin_pct: float = 10.0
    extra_parking_per_unit: int = 0
    private_debt_m: float = 30.0
    committed_equity_m: float = 15.0

NEIGHBORHOODS = {
    'Friendship Heights / Ward 3': {'market_rent': 3900, 'cost_per_unit': 590000, 'density': 160, 'tagline': 'Higher illustrative rents and land/development costs; transit access.'},
    'Columbia Heights / Ward 1': {'market_rent': 3200, 'cost_per_unit': 490000, 'density': 200, 'tagline': 'Transit-rich mixed-use area with competing neighborhood needs.'},
    'Congress Heights / Ward 8': {'market_rent': 2600, 'cost_per_unit': 420000, 'density': 180, 'tagline': 'Lower illustrative market rents; financing can remain challenging.'},
}

PRESETS = {
    'Balanced mixed-income': dict(affordable_pct=30, affordable_rent=1500, grant_m=15.0, loan_m=0.0),
    'Housing supply first': dict(affordable_pct=10, affordable_rent=1500, grant_m=5.0, loan_m=0.0),
    'Deep affordability': dict(affordable_pct=100, affordable_rent=850, grant_m=30.0, loan_m=0.0),
}

def annuity_payment(principal, rate_pct, years):
    if principal < 0 or years <= 0 or rate_pct < 0:
        raise ValueError('Invalid loan terms')
    if principal == 0:
        return 0.0
    rate = rate_pct / 100
    return principal / years if rate == 0 else principal * rate / (1 - (1 + rate) ** -years)

def analyze(p: Inputs) -> dict:
    if not 1 <= p.units <= 2000 or not 0 <= p.affordable_pct <= 100:
        raise ValueError('Invalid units or affordable share')
    if any(v < 0 for v in [p.market_rent,p.affordable_rent,p.cost_per_unit,p.grant_m,p.land_credit_m,p.loan_m,p.extra_parking_per_unit,p.return_margin_pct,p.private_debt_m,p.committed_equity_m]):
        raise ValueError('Negative input')
    if not 0 <= p.vacancy_pct < 100 or not 0 <= p.opex_pct < 100 or p.cap_rate_pct <= 0:
        raise ValueError('Invalid operating assumptions')
    restricted = round(p.units*p.affordable_pct/100)
    gross = 12*((p.units-restricted)*p.market_rent+restricted*p.affordable_rent)
    egi = gross*(1-p.vacancy_pct/100)
    noi = egi*(1-p.opex_pct/100)
    value = noi/(p.cap_rate_pct/100)
    gross_cost = p.units*(p.cost_per_unit+p.extra_parking_per_unit)
    land_credit = min(gross_cost,p.land_credit_m*1e6)
    net_cost = gross_cost-land_credit
    grant = p.grant_m*1e6
    loan = p.loan_m*1e6
    loan_ds = annuity_payment(loan,p.loan_rate_pct,p.loan_years)
    # Unlevered value is independent of the capital stack. Public debt service
    # MUST NEVER be subtracted from NOI before capitalization.
    economic_gap = net_cost*(1+p.return_margin_pct/100) - grant - value
    gap = net_cost-grant-value
    private_debt=p.private_debt_m*1e6
    committed_equity=p.committed_equity_m*1e6
    capital_gap=net_cost-grant-loan-private_debt-committed_equity
    coverage=noi/loan_ds if loan_ds else None
    return {**asdict(p),'restricted_units':restricted,'market_units':p.units-restricted,
        'gross_rent':gross,'egi':egi,'noi':noi,'stabilized_value':value,'gross_cost':gross_cost,
        'land_credit':land_credit,'net_cost':net_cost,'grant':grant,'loan':loan,
        'annual_public_loan_payment':loan_ds,'residual_noi':noi-loan_ds,
        'residual_value':value, # legacy alias: unlevered, do not present as after-debt value
        'basic_gap':gap,'margin_gap':economic_gap,'economic_gap':economic_gap,
        'ds_coverage':coverage,'public_loan_dscr':coverage,
        'private_debt':private_debt,'committed_equity':committed_equity,
        'capital_stack_gap':capital_gap,
        'meets_simple_test':economic_gap<=0,
        'grant_per_restricted_home':grant/restricted if restricted else None}

def neighborhood_inputs(name, scenario='Balanced mixed-income'):
    n=NEIGHBORHOODS[name]
    return replace(Inputs(),units=n['density'],market_rent=n['market_rent'],cost_per_unit=n['cost_per_unit'],**PRESETS[scenario])

def income_examples(ami_four_person=165000, household=4):
    """Illustrative fixed income baseline, NOT HUD limits; 30% of monthly gross income."""
    if ami_four_person <= 0 or household <= 0:
        raise ValueError('Invalid household input')
    # Does not interpolate official HUD household-size adjustments.
    return [{'label':f'{pct}% of assumed AMI','income':ami_four_person*pct/100,
             'rent_budget':ami_four_person*pct/100*.30/12} for pct in (30,60,80,100)]

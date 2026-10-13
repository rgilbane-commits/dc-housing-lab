"""DC Housing Lab: transparent illustrative project finance model, not investment advice."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Inputs:
    units: int = 200
    affordable_pct: int = 30
    market_rent: int = 3000
    affordable_rent: int = 1500
    cost_per_unit: int = 450000
    subsidy_m: float = 15.0
    vacancy_pct: float = 7.0
    opex_pct: float = 40.0
    cap_rate_pct: float = 5.5
    parking_spaces_per_unit: float = 0.5
    parking_cost_per_space: int = 0  # incremental only; initial all-in cost already includes standard parking
    public_land_credit_m: float = 0.0  # reduction in land cost; not cash grant


def analyze(p: Inputs) -> dict:
    if not 1 <= p.units <= 2000 or not 0 <= p.affordable_pct <= 100:
        raise ValueError('Invalid unit count or affordable percentage')
    if p.market_rent < 0 or p.affordable_rent < 0 or p.cost_per_unit < 0:
        raise ValueError('Rents and costs must be nonnegative')
    if not (0 <= p.vacancy_pct < 100 and 0 <= p.opex_pct < 100 and p.cap_rate_pct > 0):
        raise ValueError('Invalid underwriting rates')
    if min(p.subsidy_m, p.public_land_credit_m, p.parking_spaces_per_unit, p.parking_cost_per_space) < 0:
        raise ValueError('Public support and parking costs must be nonnegative')
    affordable_units = round(p.units * p.affordable_pct / 100)
    market_units = p.units - affordable_units
    gross = 12 * (market_units*p.market_rent + affordable_units*p.affordable_rent)
    egi = gross * (1 - p.vacancy_pct / 100)
    noi = egi * (1 - p.opex_pct / 100)
    value = noi / (p.cap_rate_pct / 100)
    parking_cost = p.units * p.parking_spaces_per_unit * p.parking_cost_per_space
    gross_tdc = p.units*p.cost_per_unit + parking_cost
    land_credit = min(gross_tdc, p.public_land_credit_m*1e6)
    net_tdc = gross_tdc - land_credit
    grant = p.subsidy_m * 1e6
    gap = net_tdc - grant - value
    return {
        **asdict(p), 'affordable_units': affordable_units, 'market_units': market_units,
        'gross_revenue': gross, 'effective_revenue': egi, 'noi': noi, 'stabilized_value': value,
        'parking_increment': parking_cost, 'gross_tdc': gross_tdc, 'land_credit': land_credit,
        'net_tdc': net_tdc, 'capital_subsidy': grant, 'funding_gap': gap,
        'support_per_affordable_unit': (grant+land_credit)/affordable_units if affordable_units else None,
        'yield_on_cost': noi/net_tdc if net_tdc else None,
        'feasible_proxy': gap <= 0,
    }


def optimal_subsidy_m(p: Inputs) -> float:
    r = analyze(p)
    return max(0.0, (r['net_tdc'] - r['stabilized_value'])/1e6)

PRESETS = {
    'Baseline: mixed-income near Metro': Inputs(),
    'Supply-first: more density': Inputs(units=300, affordable_pct=10, subsidy_m=10),
    'Deep affordability: higher public cost': Inputs(units=150, affordable_pct=100, affordable_rent=1250, subsidy_m=40),
    'High-cost neighborhood': Inputs(units=120, affordable_pct=25, cost_per_unit=600000, market_rent=3800, subsidy_m=10),
}

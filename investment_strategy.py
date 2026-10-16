"""Illustrative public capital allocation; does not imply any housing units are delivered."""
from dataclasses import dataclass
from math import floor, isfinite

AREAS = ('Rock Creek West', 'Mid-City', 'Far Southeast and Southwest')
STRATEGIES = ('New construction', 'Preservation', 'Deep affordability', 'Mixed-income')

# Explicitly assumed public contribution per home, NOT construction cost, observed DC awards, or guaranteed outcomes.
SUBSIDY_PER_HOME = {
    'New construction': 250_000.0,
    'Preservation': 110_000.0,
    'Deep affordability': 425_000.0,
    'Mixed-income': 175_000.0,
}

@dataclass(frozen=True)
class Line:
    area: str
    strategy: str
    allocation_m: float
    support_per_home: float
    capital_gate: bool = False
    operations_gate: bool = False
    eligibility_gate: bool = False


def evaluate(lines, budget_m=100.0):
    if not isfinite(budget_m) or budget_m <= 0: raise ValueError('Budget must be positive and finite')
    results=[]; spent=0.0; potential=0; validated=0
    seen=set()
    for line in lines:
        if line.area not in AREAS or line.strategy not in STRATEGIES:
            raise ValueError('Unknown planning area or housing strategy')
        key=(line.area,line.strategy)
        if key in seen: raise ValueError('Duplicate allocation line')
        seen.add(key)
        if (not isfinite(line.allocation_m) or line.allocation_m < 0 or
                not isfinite(line.support_per_home) or line.support_per_home <= 0):
            raise ValueError('Invalid allocation or per-home subsidy')
        allocated=line.allocation_m*1_000_000.0
        homes=floor((allocated + 1e-8)/line.support_per_home)
        used=homes*line.support_per_home
        unassigned=allocated-used
        qualified=bool(line.capital_gate and line.operations_gate and line.eligibility_gate)
        potential+=homes
        if qualified: validated+=homes
        spent+=allocated
        results.append({'planning_area':line.area, 'strategy':line.strategy,
                        'allocation_m':line.allocation_m, 'assumed_support_per_home':line.support_per_home,
                        'illustrative_home_capacity':homes,'unassigned_fractional_budget':round(unassigned,2),
                        'capital_confirmed':line.capital_gate,'operations_confirmed':line.operations_gate,
                        'eligibility_confirmed':line.eligibility_gate,
                        'all_gates_confirmed':qualified,
                        'qualified_illustrative_capacity':homes if qualified else 0,
                        'delivered_homes':0})
    if spent > budget_m*1_000_000+0.00001: raise ValueError('Allocation exceeds authorized budget')
    return {'budget_m':budget_m,'allocated_m':spent/1_000_000,
            'unallocated_m':max(0.,budget_m-spent/1_000_000),
            'potential_capacity':potential,
            'qualified_illustrative_capacity':validated,
            'delivered_homes':0,
            'lines':results,
            'warning':'Modeled capacity is hypothetical and not evidence of completed or committed housing. Qualification gates are user attestations, not documentary verification.'}

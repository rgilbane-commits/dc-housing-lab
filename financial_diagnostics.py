"""Independent, pure-function diagnostics for simplified stabilized development underwriting.

Not an appraisal, tax model, loan commitment, or investment-return projection.
"""
from math import isfinite


def diagnostics(r: dict) -> dict:
    cost = float(r['net_cost'])
    noi = float(r['noi'])
    value = float(r['stabilized_value'])
    cap = float(r['cap_rate_pct']) / 100
    if cost <= 0 or cap <= 0 or not all(isfinite(v) for v in [cost, noi, value, cap]):
        raise ValueError('Positive net cost, cap rate and finite figures required')
    grant = float(r['grant'])
    eligible = min(max(0, grant), cost)
    net_after_grant = cost-eligible
    margin = float(r['return_margin_pct'])/100
    cost_yield = noi/cost
    value_spread = value-cost
    after_grant_spread = value-net_after_grant
    yield_spread = cost_yield-cap
    debt_constraints = {
        'DSCR':float(r['private_debt_by_dscr']),
        'LTV':float(r['private_debt_by_ltv']),
        'LTC':float(r['private_debt_by_ltc']),
    }
    funding_gap = float(r['additional_equity_needed'])
    available_debt = float(r['funded_private_debt'])
    public_debt = float(r['loan'])
    total_debt_service=float(r['total_annual_debt_service'])
    safe_debt_service=noi/float(r['min_total_dscr'])
    check = abs(value-noi/cap)<0.01
    if not check:
        raise ValueError('Financial diagnostics received inconsistent NOI, value or cap rate')
    return {
        'yield_on_cost_pct':100*cost_yield,
        'exit_cap_pct':100*cap,
        'yield_cap_spread_bps':10000*yield_spread,
        'unsubsidized_value_creation':value_spread,
        'unsubsidized_value_creation_pct':100*value_spread/cost,
        'grant_offset':eligible,
        'net_cost_after_grant':net_after_grant,
        'grant_adjusted_value_headroom':after_grant_spread,
        'gross_cost_margin_hurdle':cost*(1+margin),
        'legacy_hurdle_headroom':value+grant-cost*(1+margin),
        'net_cost_margin_hurdle':net_after_grant*(1+margin),
        'net_cost_hurdle_headroom':value-net_after_grant*(1+margin),
        'debt_constraints':debt_constraints,
        'private_debt_capacity':float(r['private_debt_capacity']),
        'private_debt_used':available_debt,
        'public_loan':public_debt,
        'dscr_supported':bool(r['public_loan_supported']) and total_debt_service <= safe_debt_service + 1e-6,
        'dscr_headroom_annual':safe_debt_service-total_debt_service,
        'additional_equity_needed':funding_gap,
        'equity_required':float(r['equity_required']),
        'committed_equity':float(r['committed_equity']),
        'economic_value_positive': value_spread>=0,
        'funding_complete':funding_gap<=0.01 and float(r['excess_financing_sources'])<=0.01,
        'unsubsidized_yield_advantage':yield_spread>0,
        'warning': 'Net development cost reflects assumed land-credit reduction; it may not equal all-in economic or appraisal basis. Grant eligibility and realized sale proceeds are unverified.',
    }


def chart_data(d: dict) -> dict:
    """Pure chart series; no chart recalculation independent of metrics."""
    return {
        'value_bridge': [
            {'Measure':'Net development cost','Amount ($)':d['net_cost_after_grant']+d['grant_offset']},
            {'Measure':'Assumed grant offset','Amount ($)':d['grant_offset']},
            {'Measure':'Cost after grant','Amount ($)':d['net_cost_after_grant']},
            {'Measure':'Stabilized value','Amount ($)':d['unsubsidized_value_creation']+d['net_cost_after_grant']+d['grant_offset']},
        ],
        'debt_limits': [{'Constraint': k, 'Private debt ($)': v} for k,v in d['debt_constraints'].items()],
        'yield': [{'Metric':'Yield on cost','Percent':d['yield_on_cost_pct']},{'Metric':'Exit cap','Percent':d['exit_cap_pct']}],
    }

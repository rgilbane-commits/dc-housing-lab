"""v1.3 classroom exploration helpers; hypothetical assumptions only."""
from dataclasses import asdict, replace
from model import Inputs, analyze

SHOCKS = {
    'Construction cost +15%': 'cost',
    'Cap rate +0.75 percentage points': 'cap',
    'Allowable apartments -20%': 'density',
    'Grant funding reduced by half': 'grant',
}

def shock(p: Inputs, label: str) -> Inputs:
    if label == 'Construction cost +15%':
        return replace(p, cost_per_unit=int(round(p.cost_per_unit*1.15/25000)*25000))
    if label == 'Cap rate +0.75 percentage points':
        return replace(p,cap_rate_pct=round(min(9.0,p.cap_rate_pct+.75)*4)/4)
    if label == 'Allowable apartments -20%':
        return replace(p,units=max(50,int(round(p.units*.8/10)*10)))
    if label == 'Grant funding reduced by half':
        return replace(p,grant_m=round(p.grant_m*.5))
    raise ValueError('Unknown classroom shock')

def sensitivity(p: Inputs, cost_changes=(-.10,0,.10), cap_changes=(-.5,0,.5)):
    output=[]
    for delta in cost_changes:
        row={'Cost change': f'{delta:+.0%}'}
        for shift in cap_changes:
            cap=max(.25,p.cap_rate_pct+shift)
            other=replace(p,cost_per_unit=p.cost_per_unit*(1+delta),cap_rate_pct=cap)
            row[f'{cap:.2f}% cap']=analyze(other)['margin_gap']
        output.append(row)
    return output

def minimum_grant_to_margin(p: Inputs):
    # Required grant holding all non-grant assumptions fixed, capped only in UI.
    other=replace(p,grant_m=0)
    return max(0.0,analyze(other)['margin_gap'])

def snapshot(p: Inputs, title: str):
    r=analyze(p)
    return {'Name':title, 'Homes':r['units'],'Affordable homes':r['restricted_units'],
            'Affordable share (%)':100*r['restricted_units']/r['units'],
            'Affordable rent ($/mo)':p.affordable_rent,
            'Annual NOI ($)':r['noi'],'Net project cost ($)':r['net_cost'],
            'Public grant ($)':r['grant'],'Public land credit ($)':r['land_credit'],
            'Public loan ($)':r['loan'],'Capital funding gap ($)':r['capital_stack_gap'],'Public loan DSCR (x)':r['public_loan_dscr'], 'Total DSCR (x)':r['total_dscr'], 'Supportable private debt ($)':r['private_debt_capacity'], 'Private debt used ($)':r['funded_private_debt'], 'Required equity ($)':r['equity_required'], 'Additional equity required ($)':r['additional_equity_needed'], 'Economic margin gap ($)':r['margin_gap'],
            'Public support per affordable home ($)': (r['grant']+r['land_credit'])/r['restricted_units'] if r['restricted_units'] else None,
            'Illustrative margin test': 'Pass' if r['meets_simple_test'] else 'Fail',
            'inputs':asdict(p)}

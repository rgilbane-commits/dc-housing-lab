"""Illustrative ten-year stabilized operating forecast. No external data."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ForecastAssumptions:
    market_growth_pct: float = 3.0
    restricted_growth_pct: float = 1.5
    expense_inflation_pct: float = 3.5
    vacancy_pct: float = 7.0
    annual_reserve_per_unit: float = 400.0
    exit_cap_pct: float = 6.0
    selling_cost_pct: float = 2.0

def _amortization(balance, rate_pct, amort_years, years=10):
    if balance <= 0: return [(0.0,0.0)]*years
    if amort_years <= 0 or rate_pct < 0: raise ValueError('Invalid debt terms')
    rate=rate_pct/100
    payment=balance/amort_years if not rate else balance*rate/(1-(1+rate)**(-amort_years))
    output=[]
    for year in range(years):
        if balance < 1e-6:
            output.append((0.0,0.0)); continue
        interest=balance*rate
        debt_service=min(payment,balance+interest)
        balance=max(0.0,balance+interest-debt_service)
        output.append((debt_service,balance))
    return output

def _irr(flows):
    if not flows or flows[0]>=0 or not any(c>0 for c in flows[1:]):return None
    def npv(r):return sum(cf/(1+r)**i for i,cf in enumerate(flows))
    lower=-0.999; upper=1.0
    while npv(upper)>0 and upper<1e5: upper=upper*2+1
    if npv(lower)*npv(upper)>0:return None
    for _ in range(180):
        mid=(lower+upper)/2
        if npv(mid)>0:lower=mid
        else:upper=mid
    result=(lower+upper)/2
    return result if isfinite(result) else None

def project(p,r,a=ForecastAssumptions()):
    for rate in (a.market_growth_pct,a.restricted_growth_pct,a.expense_inflation_pct):
        if not -50<=rate<=50:raise ValueError('Annual growth rate outside allowed range')
    if not 0<=a.vacancy_pct<100 or a.exit_cap_pct<=0 or not 0<=a.selling_cost_pct<100 or a.annual_reserve_per_unit<0:
        raise ValueError('Invalid forecast settings')
    market_annual=r['market_units']*p.market_rent*12
    restricted_annual=r['restricted_units']*p.affordable_rent*12
    base_opex=r['egi']-r['noi']
    public_schedule=_amortization(r['loan'],p.loan_rate_pct,p.loan_years)
    private_schedule=_amortization(r['funded_private_debt'],p.private_rate_pct,p.private_amort_years)
    rows=[]
    for year in range(1,12):
        scheduled=market_annual*(1+a.market_growth_pct/100)**(year-1)+restricted_annual*(1+a.restricted_growth_pct/100)**(year-1)
        egi=scheduled*(1-a.vacancy_pct/100)
        operating_expense=base_opex*(1+a.expense_inflation_pct/100)**(year-1)
        noi=egi-operating_expense
        if year==11:
            next_noi=noi
            break
        reserve=p.units*a.annual_reserve_per_unit*(1+a.expense_inflation_pct/100)**(year-1)
        public_ds, public_balance=public_schedule[year-1]
        private_ds, private_balance=private_schedule[year-1]
        cash_flow=noi-reserve-public_ds-private_ds
        rows.append({'year':year,'scheduled_rent':scheduled,'effective_income':egi,'operating_expenses':operating_expense,
           'noi':noi,'replacement_reserve':reserve,'public_debt_service':public_ds,'private_debt_service':private_ds,
           'total_debt_service':public_ds+private_ds,'cash_flow_to_equity':cash_flow,
           'public_balance':public_balance,'private_balance':private_balance,
           'dscr': noi/(public_ds+private_ds) if public_ds+private_ds>0 else None})
    sale_price=next_noi/(a.exit_cap_pct/100)
    selling_cost=sale_price*a.selling_cost_pct/100
    ending_debt=rows[-1]['public_balance']+rows[-1]['private_balance']
    net_sale=sale_price-selling_cost-ending_debt
    equity=r['equity_required']
    flows=[-equity]+[row['cash_flow_to_equity'] for row in rows]
    flows[-1]+=net_sale
    return {'rows':rows,'sale_price':sale_price,'selling_cost':selling_cost,'ending_debt':ending_debt,
       'net_sale_to_equity':net_sale,'year_11_noi':next_noi,'initial_equity':equity,
       'equity_multiple':sum(flows[1:])/equity if equity>0 else None,
       'equity_irr':_irr(flows) if equity>0 else None,'investor_cash_flows':flows,
       'cumulative_operating_cash':sum(x['cash_flow_to_equity'] for x in rows),
       'minimum_cash_flow':min(x['cash_flow_to_equity'] for x in rows),
       'expense_growth_exceeds_restricted_growth':a.expense_inflation_pct>a.restricted_growth_pct}

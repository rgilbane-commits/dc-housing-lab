"""Illustrative monthly construction-to-sale development cash flows.

No tax, LIHTC, contractual public-loan maturity, construction draw fee or operating
reserve funding is assumed. The model does not imply a lender commitment.
"""
from dataclasses import dataclass
from math import isfinite
from model import annuity_payment

@dataclass(frozen=True)
class DevelopmentAssumptions:
    construction_months: int = 24
    leaseup_months: int = 12
    hold_months: int = 120
    construction_loan_pct: float = 55.0
    construction_rate_pct: float = 8.0
    construction_fee_pct: float = 1.0
    private_origination_fee_pct: float = 1.0
    sale_cap_pct: float = 6.0
    sale_cost_pct: float = 2.0
    noi_growth_pct: float = 2.0
    monthly_reserve_per_home: float = 35.0


def _irr(cash):
    if not any(x < 0 for x in cash) or not any(x > 0 for x in cash):
        return None
    def npv(rate): return sum(v / ((1+rate)**i) for i,v in enumerate(cash))
    lo,hi=-0.95,1.0
    if npv(lo)*npv(hi)>0:
        return None
    for _ in range(130):
        mid=(lo+hi)/2
        if npv(lo)*npv(mid)<=0: hi=mid
        else:lo=mid
    return (lo+hi)/2


def _monthly_payment(principal, annual_rate_pct, amort_years):
    rate=annual_rate_pct/1200
    periods=amort_years*12
    if principal<=0:return 0.0
    return principal/periods if rate==0 else principal*rate/(1-(1+rate)**(-periods))


def calculate(p, r, a=DevelopmentAssumptions()):
    if not (1<=a.construction_months<=60 and 0<=a.leaseup_months<=60 and 12<=a.hold_months<=360):
        raise ValueError('Invalid construction, lease-up or hold period')
    for v in (a.construction_loan_pct,a.construction_rate_pct,a.construction_fee_pct,
              a.private_origination_fee_pct,a.sale_cost_pct,a.noi_growth_pct,a.monthly_reserve_per_home):
        if not isfinite(v) or v<0:raise ValueError('Invalid negative or nonfinite assumption')
    if not (a.construction_loan_pct<=100 and a.construction_fee_pct<=20 and
            a.private_origination_fee_pct<=20 and a.sale_cost_pct<100 and
            0<a.sale_cap_pct<=30 and a.noi_growth_pct<=30 and
            a.construction_rate_pct<=50):
        raise ValueError('Assumption outside allowed range')
    if not r['public_loan_supported'] or r['excess_financing_sources']>0.01:
        raise ValueError('Capital stack fails public loan debt coverage or overfunding gate')
    cost=r['net_cost']; grant=min(r['grant'],cost)
    const_debt_target=cost*a.construction_loan_pct/100
    const_fee=const_debt_target*a.construction_fee_pct/100
    private=r['funded_private_debt']; public=r['loan']
    perm_fee=private*a.private_origination_fee_pct/100
    flows=[0.0]; rows=[]; outstanding=0.0
    total_equity=0.0; interest_total=0.0
    # Construction: straight-line spending; loan draws cover a fixed percentage.
    for month in range(1,a.construction_months+1):
        use=cost/a.construction_months
        grant_draw=grant/a.construction_months
        draw=const_debt_target/a.construction_months
        outstanding+=draw
        interest=outstanding*a.construction_rate_pct/1200
        interest_total+=interest
        fee=const_fee if month==1 else 0.0
        equity=use+interest+fee-grant_draw-draw
        # Avoid negative construction equity if grant + construction proceeds exceed spending.
        if equity < -0.01:
            raise ValueError('Construction draws exceed project uses; reduce construction loan share')
        equity=max(0.0,equity)
        total_equity+=equity
        flows.append(-equity)
        rows.append({'month':month,'phase':'Construction','development_uses':use,'grant_draw':grant_draw,
                     'construction_debt_draw':draw,'construction_interest':interest,'construction_debt_balance':outstanding,
                     'private_debt_balance':0.0,'public_debt_balance':0.0,'noi':0.0,
                     'net_equity_cash_flow':-equity})
    # At completion the permanent loan and public loan pay off the construction loan.
    net_refi=private+public-outstanding-perm_fee
    flows[-1]+=net_refi
    rows[-1]['net_equity_cash_flow']+=net_refi
    rows[-1]['refinancing_net_proceeds']=net_refi
    rows[-1]['private_debt_balance']=private
    rows[-1]['public_debt_balance']=public
    # Operation: conservative ramp to modeled stabilized NOI over the lease-up period.
    pri_balance=private; pub_balance=public
    pri_pay=_monthly_payment(private,p.private_rate_pct,p.private_amort_years)
    pub_pay=_monthly_payment(public,p.loan_rate_pct,p.loan_years)
    initial_noi=r['noi']
    min_operating=0.0
    for operating_month in range(1,a.hold_months+1):
        month=a.construction_months+operating_month
        occupancy_factor=min(1.0,operating_month/a.leaseup_months) if a.leaseup_months else 1.0
        noi=(initial_noi/12)*((1+a.noi_growth_pct/100)**((operating_month-1)/12))*occupancy_factor
        reserve=p.units*a.monthly_reserve_per_home
        interest_pri=pri_balance*p.private_rate_pct/1200
        interest_pub=pub_balance*p.loan_rate_pct/1200
        pri_ds=min(pri_pay,pri_balance+interest_pri)
        pub_ds=min(pub_pay,pub_balance+interest_pub)
        pri_balance=max(0.0,pri_balance+interest_pri-pri_ds)
        pub_balance=max(0.0,pub_balance+interest_pub-pub_ds)
        op_cash=noi-reserve-pri_ds-pub_ds
        min_operating=min(min_operating,op_cash)
        flows.append(op_cash)
        rows.append({'month':month,'phase':'Operations','development_uses':0.0,'grant_draw':0.0,
                     'construction_debt_draw':0.0,'construction_interest':0.0,'construction_debt_balance':0.0,
                     'private_debt_balance':pri_balance,'public_debt_balance':pub_balance,'noi':noi,
                     'net_equity_cash_flow':op_cash})
    next_year_noi=initial_noi*((1+a.noi_growth_pct/100)**(a.hold_months/12))
    if next_year_noi<=0:
        sale=None; net_sale=None; irr=None; multiple=None
    else:
        sale=next_year_noi/(a.sale_cap_pct/100)
        net_sale=sale*(1-a.sale_cost_pct/100)-pri_balance-pub_balance
        flows[-1]+=net_sale
        rows[-1]['net_equity_cash_flow']+=net_sale
        monthly_irr=_irr(flows)
        irr=(1+monthly_irr)**12-1 if monthly_irr is not None else None
        invested=-sum(min(0.0,cf) for cf in flows)
        distributed=sum(max(0.0,cf) for cf in flows)
        multiple=distributed/invested if invested>0 else None
    return {'rows':rows,'cash_flows':flows,'construction_interest':interest_total,
            'construction_loan_peak':const_debt_target,'construction_fee':const_fee,
            'permanent_loan_fee':perm_fee,'total_development_uses_including_finance':cost+interest_total+const_fee+perm_fee,
            'equity_contributed_during_construction':total_equity,'net_permanent_financing_proceeds':net_refi,
            'ending_private_debt':pri_balance,'ending_public_debt':pub_balance,
            'terminal_noi':next_year_noi,'sale_value':sale,'net_sale_to_equity':net_sale,
            'levered_irr':irr,'equity_multiple':multiple,'minimum_operating_cash':min_operating,
            'financing_screen_passed':bool(r['financing_feasible']),
            'unfunded_equity_at_stabilization':r['additional_equity_needed'],
            'warning':'Scenario requires additional equity; modeled cash flows assume it is contributed.' if r['additional_equity_needed']>0 else ''}

"""Monthly development investment dashboard; exclusively consumes calculated outputs."""
import pandas as pd
import streamlit as st
from dataclasses import replace
from development_returns import DevelopmentAssumptions, calculate


def render(p,r):
    st.subheader('Construction-to-sale returns | monthly model')
    st.caption('Illustrative unlevered project costs, monthly construction financing, permanent takeout, operating ramp and sale. Not a commitment, tax-credit model, or sponsor/investor waterfall.')
    a=DevelopmentAssumptions()
    c1,c2,c3=st.columns(3)
    with c1:
        months=st.slider('Construction period (months)',6,48,a.construction_months,1,key='ret_construction')
        leaseup=st.slider('Lease-up period (months)',0,36,a.leaseup_months,1,key='ret_leaseup')
        hold=st.slider('Operating hold (years)',3,20,a.hold_months//12,1,key='ret_hold')
    with c2:
        const_share=st.slider('Construction loan / net cost (%)',0,80,int(a.construction_loan_pct),5,key='ret_const_share')
        const_rate=st.slider('Construction interest (%)',0.0,18.0,a.construction_rate_pct,0.5,key='ret_const_rate')
        const_fee=st.slider('Construction loan fee (%)',0.0,5.0,a.construction_fee_pct,0.25,key='ret_const_fee')
        perm_fee=st.slider('Permanent debt origination fee (%)',0.0,5.0,a.private_origination_fee_pct,0.25,key='ret_perm_fee')
    with c3:
        cap=st.slider('Disposition cap rate (%)',3.0,10.0,a.sale_cap_pct,0.25,key='ret_exit_cap')
        growth=st.slider('Annual NOI growth (%)',0.0,8.0,a.noi_growth_pct,0.25,key='ret_noi_growth')
        sale_cost=st.slider('Sale costs (%)',0.0,8.0,a.sale_cost_pct,0.25,key='ret_sale_cost')
        reserves=st.slider('Monthly reserves / home ($)',0.0,120.0,a.monthly_reserve_per_home,5.0,key='ret_reserves')
    a=replace(a,construction_months=months,leaseup_months=leaseup,hold_months=hold*12,
              construction_loan_pct=const_share,construction_rate_pct=const_rate,construction_fee_pct=const_fee,
              private_origination_fee_pct=perm_fee,sale_cap_pct=cap,noi_growth_pct=growth,
              sale_cost_pct=sale_cost,monthly_reserve_per_home=reserves)
    try:
        result=calculate(p,r,a)
    except ValueError as exc:
        st.error(f'Monthly investment scenario unavailable: {exc}')
        return
    # The v2.7.1+ dashboard and returns calculation must be deployed together.
    # An older deployed development_returns.py lacks the metrics below; refuse
    # to display a partially compatible result instead of raising KeyError.
    required_metrics = ('operating_deficit_total', 'operating_deficit_months',
                        'refinance_equity_call', 'levered_irr', 'equity_multiple',
                        'construction_interest', 'net_sale_to_equity', 'warning',
                        'minimum_operating_cash', 'financing_screen_passed', 'rows')
    missing_metrics = [key for key in required_metrics if key not in result]
    if missing_metrics:
        st.error('Development Returns version mismatch: the deployed returns engine '
                 'does not supply the metrics required by this dashboard. '
                 'Replace BOTH development_returns.py and '
                 'development_returns_dashboard.py from the same v2.7.3 release, '
                 'then reboot the Streamlit app. Missing: '
                 + ', '.join(missing_metrics))
        return
    def millions(value):return f'${value/1e6:,.2f}M' if value is not None else 'N/A'
    d1,d2,d3,d4=st.columns(4)
    d1.metric('Levered annualized IRR',f"{result['levered_irr']*100:.1f}%" if result['levered_irr'] is not None else 'N/A')
    d2.metric('Equity multiple',f"{result['equity_multiple']:.2f}×" if result['equity_multiple'] is not None else 'N/A')
    d3.metric('Construction interest',millions(result['construction_interest']))
    d4.metric('Net sale proceeds',millions(result['net_sale_to_equity']))
    k1,k2,k3=st.columns(3)
    k1.metric('Lease-up / operations deficit funding',millions(result['operating_deficit_total']))
    k2.metric('Months requiring operating cash support',str(result['operating_deficit_months']))
    k3.metric('Equity required at construction takeout',millions(result['refinance_equity_call']))
    if result['warning']:st.warning(result['warning'])
    if result['minimum_operating_cash'] < 0:st.warning('At least one month has negative cash after operating expenses, reserves and debt service.')
    if not result['financing_screen_passed']:st.error('Financing screen is not satisfied; displayed returns assume the necessary equity is funded.')
    data=pd.DataFrame(result['rows'])
    st.markdown('#### Financing balances and monthly capital requirements')
    st.line_chart(data.set_index('month')[['construction_debt_balance','private_debt_balance','public_debt_balance']],x_label='Month',y_label='Debt outstanding ($)')
    st.bar_chart(data.set_index('month')['net_equity_cash_flow'],x_label='Month',y_label='Net cash to equity ($)')
    st.markdown('#### Exit capitalization × construction cost sensitivity')
    cap_shocks=[-1.0,-0.5,0,0.5,1.0]
    cost_shocks=[-10,-5,0,5,10]
    matrix=[]
    # Cost sensitivity re-runs the actual model; existing debt sizing is recalculated.
    from model import analyze
    for cost_change in cost_shocks:
        new_p=replace(p,cost_per_unit=round(p.cost_per_unit*(1+cost_change/100)))
        rr=analyze(new_p)
        line={'Cost change':f'{cost_change:+d}%'}
        for cap_change in cap_shocks:
            candidate=replace(a,sale_cap_pct=a.sale_cap_pct+cap_change)
            try:
                z=calculate(new_p,rr,candidate)
                line[f'{cap_change:+.1f}pp']=None if z['levered_irr'] is None else 100*z['levered_irr']
            except ValueError:line[f'{cap_change:+.1f}pp']=None
        matrix.append(line)
    df=pd.DataFrame(matrix).set_index('Cost change')
    # Avoid Styler.background_gradient: it requires optional matplotlib at runtime.
    # Only display colors change; sensitivity values continue to come from calculate().
    def irr_cell_style(value):
        if pd.isna(value):
            return 'background-color: #e5e7eb; color: #374151'
        # Deliberately fixed, interpretable annual IRR bands rather than a
        # scenario-relative scale that can make weak results appear strong.
        if value < 0:
            return 'background-color: #f6cac6; color: #50251f'
        if value < 5:
            return 'background-color: #f7ded1; color: #503222'
        if value < 10:
            return 'background-color: #f8eed2; color: #4c4229'
        if value < 15:
            return 'background-color: #e2edd9; color: #264330'
        return 'background-color: #cae8d6; color: #204b36'
    styled=df.style.format('{:.1f}%',na_rep='N/A').map(irr_cell_style)
    st.dataframe(styled,use_container_width=True)
    st.caption('IRR matrix in percentage terms. Each case re-underwrites project cost and permanent debt capacity. Cells are unavailable when financing constraints invalidate the scenario. A positive IRR is not evidence of lender approval or fundable equity.')
    export=data.copy()
    st.download_button('Download monthly cash-flow ledger (CSV)',export.to_csv(index=False).encode('utf-8'),file_name='dc_housing_lab_monthly_development_returns.csv',mime='text/csv',key='returns_monthly_csv')
    st.caption('IRR is suppressed if more than one mathematical root exists within the modeled monthly rate range (−99% to +200%). Negative operating cash flow is represented as incremental equity funding; no separate liquidity reserve is modeled.')
    st.caption('Important: Construction and permanent financing are simplified. The engine excludes taxes, capital-call dates, LIHTC installments, promote waterfalls, refinance covenants, lease-up concessions, and cash-trap mechanisms. A return computed on modeled equity does not establish achievable investor returns.')

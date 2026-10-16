"""Display-only financial sensitivity page; pure calculation in profitability_sensitivity."""
import pandas as pd
import streamlit as st
from profitability_sensitivity import Stress, run_case, matrix, break_even_market_rent

METRICS={'Value less cost':'value_spread','Net-cost hurdle gap':'net_cost_hurdle_gap',
         'Additional equity needed':'additional_equity','Private debt capacity':'private_debt_capacity'}

def _heat_colors(data, bad=False):
    """Dependency-free color scale: high values unfavorable for gaps, favorable otherwise."""
    lo=float(data.min().min()); hi=float(data.max().max())
    result=pd.DataFrame('',index=data.index,columns=data.columns)
    for i in data.index:
        for j in data.columns:
            q=(float(data.loc[i,j])-lo)/(hi-lo) if hi>lo else .5
            good=1-q if bad else q
            # Modest red-to-teal tint with readable foreground in either theme.
            red=int(245-34*good);green=int(226+13*good);blue=int(222+13*good)
            result.loc[i,j]=f'background-color: rgb({red},{green},{blue}); color: #203040'
    return result

def render(p, fm):
    st.markdown('### Profitability & stress-testing studio')
    st.caption('All figures recomputed with the existing development financial engine. Market-rent shocks apply only to market-rate homes; regulated rents stay fixed. No land repricing, lease-up, sale transaction costs or construction timing changes are assumed.')
    c1,c2,c3,c4=st.columns(4)
    cost=c1.slider('Construction / cost shock',-30,50,0,5,key='v260_cost')
    rent=c2.slider('Market-rent shock',-30,50,0,5,key='v260_rent')
    cap=c3.slider('Exit cap-rate shift (bps)',-200,300,0,25,key='v260_cap')
    interest=c4.slider('Private interest-rate shift (bps)',-300,400,0,25,key='v260_rate')
    try:
        base=run_case(p,Stress())
        current=run_case(p,Stress(cost,rent,cap,interest))
    except ValueError as ex:
        st.error(str(ex));return
    q1,q2,q3,q4=st.columns(4)
    q1.metric('Value less net cost',fm(current['value_spread']),delta=fm(current['value_spread']-base['value_spread']))
    q2.metric('Additional equity required',fm(current['additional_equity']),delta=fm(current['additional_equity']-base['additional_equity']),delta_color='inverse')
    q3.metric('Private debt capacity',fm(current['private_debt_capacity']),delta=fm(current['private_debt_capacity']-base['private_debt_capacity']))
    q4.metric('Net-cost hurdle gap',fm(current['net_cost_hurdle_gap']),delta=fm(current['net_cost_hurdle_gap']-base['net_cost_hurdle_gap']),delta_color='inverse')
    if not current['dscr_supported']:
        st.error('Debt coverage fails the selected minimum DSCR under this scenario.')
    if not current['economic_hurdle_met']:
        st.warning('Subsidy-adjusted economic hurdle not satisfied. This is distinct from the equity funding gap.')
    if not current['financing_feasible']:
        st.info('Financing not fully supported by the modeled debt capacity and committed equity.')
    st.markdown('#### Cost × market-rent sensitivity')
    left,right=st.columns([1,2])
    with left:
        display=st.selectbox('Heatmap measure',list(METRICS),key='v260_metric')
        st.caption('Rows: cost change. Columns: market-rent change. Cap-rate and interest shifts match the controls above.')
        st.caption('Economic values are signed dollar amounts; additional equity and debt capacity are financing measures.')
    cases=matrix(p,cap_bps=cap,private_rate_bps=interest)
    key=METRICS[display]
    table=pd.DataFrame([[case[key]/1e6 for case in row] for row in cases],
                       index=[f'{v:+d}%' for v in (-15,-10,-5,0,5,10,15)],
                       columns=[f'{v:+d}%' for v in (-15,-10,-5,0,5,10,15)])
    table.index.name='Cost change';table.columns.name='Market rent change'
    with right:
        st.dataframe(table.style.format('${:,.2f}M').apply(_heat_colors, axis=None, bad=(key in ('net_cost_hurdle_gap','additional_equity'))),use_container_width=True)
    st.caption('Color is relative within this scenario grid, not a pass/fail indicator. Each cell recomputes NOI, valuation, DSCR-limited debt, equity and economic hurdles.')
    st.markdown('#### Economic and financing movements')
    plot=pd.DataFrame([
        {'Metric':'Stabilized value','Base':base['value']/1e6,'Stressed':current['value']/1e6},
        {'Metric':'Net development cost','Base':base['net_cost']/1e6,'Stressed':current['net_cost']/1e6},
        {'Metric':'Private debt capacity','Base':base['private_debt_capacity']/1e6,'Stressed':current['private_debt_capacity']/1e6},
        {'Metric':'Equity required','Base':base['equity_required']/1e6,'Stressed':current['equity_required']/1e6},
    ]).set_index('Metric')
    st.bar_chart(plot,horizontal=True)
    st.caption('Chart amounts in $ millions. Equity required reflects supportable (not merely requested) debt. Cap rate affects property value and debt sizing; interest rate affects DSCR sizing.')
    required=break_even_market_rent(p,target='value_cost')
    r2=break_even_market_rent(p,target='net_cost_hurdle')
    c1,c2=st.columns(2)
    c1.metric('Market rent for value = net cost',f'${required:,.0f}/mo' if required is not None else 'Not applicable')
    c2.metric('Market rent for net-cost hurdle',f'${r2:,.0f}/mo' if r2 is not None else 'Not applicable')
    st.caption('Break-even rents hold other baseline inputs fixed, including affordable rents and cap rate. They test economic thresholds only; they do not certify project financing or development profit.')
    records=[]
    for c,row in zip((-15,-10,-5,0,5,10,15),cases):
        for t,s in zip((-15,-10,-5,0,5,10,15),row):
            records.append({'Cost shock (%)':c,'Market rent shock (%)':t,'Cap shift (bps)':cap,'Rate shift (bps)':interest,
              'NOI ($)':s['noi'],'Value ($)':s['value'],'Net cost ($)':s['net_cost'],
              'Value less cost ($)':s['value_spread'],'Net-cost margin gap ($)':s['net_cost_hurdle_gap'],
              'Private debt capacity ($)':s['private_debt_capacity'],'Additional equity ($)':s['additional_equity'],
              'DSCR supported':s['dscr_supported'],'Financing feasible':s['financing_feasible'],
              'Economic hurdle met':s['economic_hurdle_met'],'Both screens passed':s['screen_pass']})
    st.download_button('Download 49-case sensitivity matrix (CSV)',pd.DataFrame(records).to_csv(index=False),
       file_name='dc_housing_lab_v2_6_0_sensitivity.csv',mime='text/csv',key='v260_csv')

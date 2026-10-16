"""Presentation-only financial diagnostics. Reads already calculated model outputs."""
import pandas as pd
import streamlit as st
from financial_diagnostics import diagnostics, chart_data


def render_financial_diagnostics(r, fm):
    d=diagnostics(r)
    plots=chart_data(d)
    st.markdown('### Development feasibility diagnostics')
    st.caption('Illustrative stabilized, unlevered economics. Grant eligibility, land value and asset sale proceeds are not independently verified.')
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Yield on net cost',f"{d['yield_on_cost_pct']:.2f}%",help='Stabilized NOI ÷ net development cost after the assumed land credit; before any grant.')
    c2.metric('Exit capitalization rate',f"{d['exit_cap_pct']:.2f}%")
    c3.metric('Yield–cap spread',f"{d['yield_cap_spread_bps']:+,.0f} bps",help='Yield on cost minus exit cap rate; not an equity return.')
    c4.metric('Value creation before grant',fm(d['unsubsidized_value_creation']),help='Capitalized NOI less net development cost; no developer-profit or transaction-cost assumption.')
    if not d['economic_value_positive']:
        st.warning('Stabilized property value is below assumed development cost before subsidy. A grant can improve the funding position but does not change NOI-based asset value.')
    if not d['unsubsidized_yield_advantage']:
        st.info('Yield on cost does not exceed the selected exit cap rate. This is an illustrative spread test, not a complete development approval rule.')
    st.markdown('#### Value versus cost and subsidy')
    chart=pd.DataFrame(plots['value_bridge']).set_index('Measure')
    st.bar_chart(chart,y='Amount ($)',horizontal=True,color='#16877f')
    x,y,z=st.columns(3)
    x.metric('Grant-adjusted value headroom',fm(d['grant_adjusted_value_headroom']),help='Stabilized value − (net cost − eligible assumed grant). Not financing surplus.')
    y.metric('Net-cost margin headroom',fm(d['net_cost_hurdle_headroom']),help='Stabilized value − (net cost − assumed eligible grant) × (1 + required margin).')
    z.metric('Legacy hurdle headroom',fm(d['legacy_hurdle_headroom']),help='Stabilized value + grant − net development cost × (1+margin).')
    st.markdown('#### Private debt capacity: binding constraints')
    debt=pd.DataFrame(plots['debt_limits']).set_index('Constraint')
    st.bar_chart(debt,y='Private debt ($)',horizontal=True,color='#326b96')
    st.caption(f"Supportable private debt: {fm(d['private_debt_capacity'])}; amount used: {fm(d['private_debt_used'])}. These are ceilings, not lender commitments.")
    a,b,c=st.columns(3)
    a.metric('Equity required',fm(d['equity_required']))
    b.metric('Additional equity needed',fm(d['additional_equity_needed']))
    c.metric('Annual DSCR headroom',fm(d['dscr_headroom_annual']),help='Maximum annual debt service at target coverage less modeled annual debt service; negative indicates a coverage breach.')
    if not d['dscr_supported']:
        st.error('Debt service is not supportable under the selected minimum total DSCR.')
    if not d['funding_complete']:
        st.warning('Committed equity and available debt do not fully reconcile to remaining development uses, or excess financing sources are present.')
    with st.expander('Definitions, limitations, and calculations'):
        st.markdown('**Yield on cost** = NOI ÷ net development cost. **Value creation** = NOI ÷ cap rate − net development cost. **Net-cost hurdle** uses an assumed eligible grant offset. **Legacy hurdle** applies margin to full net development cost before subtracting grant. None is developer fee, realized profit, or equity IRR.')
        st.caption(d['warning'])
    return d

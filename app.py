import csv
import io
import json
from datetime import datetime

import pandas as pd
import streamlit as st
from model import Inputs, PRESETS, analyze, optimal_subsidy_m

st.set_page_config(page_title='DC Housing Lab | Sidwell Friends', page_icon='🏙️', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:1.7rem;max-width:1250px}
.hero{background:linear-gradient(115deg,#112740,#17516a);padding:28px 34px;border-radius:16px;color:white;margin-bottom:18px}
.hero h1{font-size:2.5rem;margin:0;color:white}.hero p{font-size:1rem;color:#d5e8ed;margin:8px 0 0}
.note{background:#f0f5f8;color:#233543;padding:13px 16px;border-left:4px solid #267c9b;border-radius:6px}
.small{font-size:.83rem;color:#617282}
div[data-testid="stMetric"]{background:#f3f6f8;padding:13px;border-radius:9px}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🏙️ DC Housing Lab</h1><p>Who gets to live in the city? Build a project. Set housing policy. Confront the trade-offs.</p></div>', unsafe_allow_html=True)

if 'saved' not in st.session_state:
    st.session_state.saved = []
if 'preset' not in st.session_state:
    st.session_state.preset = list(PRESETS)[0]

st.sidebar.header('Your development')
preset_choice = st.sidebar.selectbox('Starting scenario', list(PRESETS), key='preset')
if st.sidebar.button('↻ Load scenario / reset sliders', use_container_width=True):
    p = PRESETS[preset_choice]
    for field in p.__dataclass_fields__:
        st.session_state[f'v_{field}'] = getattr(p, field)
    st.rerun()

base = PRESETS[preset_choice]
def state_default(field):
    key = f'v_{field}'
    if key not in st.session_state:
        st.session_state[key] = getattr(base, field)

fields = list(base.__dataclass_fields__)
for field in fields:
    state_default(field)

st.sidebar.subheader('Housing and rents')
units = st.sidebar.slider('Number of apartments', 50, 500, step=10, key='v_units')
aff = st.sidebar.slider('Income-restricted apartments (%)', 0, 100, step=5, key='v_affordable_pct')
market = st.sidebar.slider('Monthly market rent', 1500, 6000, step=100, key='v_market_rent', format='$%d')
affrent = st.sidebar.slider('Monthly restricted rent', 500, 3500, step=50, key='v_affordable_rent', format='$%d')
st.sidebar.subheader('Development and government')
cp = st.sidebar.slider('All-in development cost / home', 250000, 800000, step=25000, key='v_cost_per_unit', format='$%d')
subsidy = st.sidebar.slider('Public capital subsidy ($ million)', 0.0, 100.0, step=1.0, key='v_subsidy_m')
land_credit = st.sidebar.slider('Public land / land-cost reduction ($ million)', 0.0, 30.0, step=1.0, key='v_public_land_credit_m')
with st.sidebar.expander('Advanced underwriting / parking'):
    vacancy = st.slider('Vacancy / collection loss (%)', 0.0, 20.0, step=1.0, key='v_vacancy_pct')
    opex = st.slider('Operating expenses (% of collected rent)', 20.0, 65.0, step=1.0, key='v_opex_pct')
    cap = st.slider('Capitalization rate (%)', 3.0, 9.0, step=0.25, key='v_cap_rate_pct')
    st.caption('Parking cost input is incremental to the base all-in development cost. Do not enter the cost twice.')
    parking_ratio = st.slider('Parking spaces per apartment', 0.0, 2.0, step=0.25, key='v_parking_spaces_per_unit')
    parking_cost = st.slider('Extra cost per parking space', 0, 75000, step=5000, key='v_parking_cost_per_space', format='$%d')

p = Inputs(**{name:st.session_state['v_'+name] for name in fields})
r = analyze(p)
fmt = lambda n: f'${abs(n)/1e6:,.1f}M' if abs(n)>=1e6 else f'${abs(n):,.0f}'

intro, build, policy, compare, guide = st.tabs(['🎯 Today’s challenge', '🏗️ Build a project', '🏛️ Policy laboratory', '🗳️ Compare proposals', '📚 Teaching notes'])

with intro:
    st.subheader('Your assignment: Make Washington more affordable')
    st.write('Imagine a vacant site near a Metro station in Washington, DC. You must choose how much housing to build, how many homes to reserve for lower-income households, and how to finance the project.')
    a,b,c = st.columns(3)
    a.info('**1. Housing supply**\n\nCan you deliver at least **200 apartments**?')
    b.info('**2. Affordability**\n\nCan you provide at least **60 income-restricted apartments**?')
    c.info('**3. Feasibility**\n\nCan you cover the modeled development cost using stabilized value and available public support?')
    checks = [r['units']>=200,r['affordable_units']>=60,r['feasible_proxy']]
    st.progress(sum(checks)/3, text=f'{sum(checks)} of 3 challenge goals achieved')
    if all(checks):
        st.success('You met all three modeled goals. Now defend the cost to taxpayers, feasibility assumptions, and who qualifies for the affordable homes.')
    else:
        st.warning('Trade-offs ahead. Adjust the project using the sidebar, and see whether you can meet all three goals.')
    st.markdown('**Discussion prompt:** Should a neighborhood with excellent transit and schools be required to accommodate more housing?')
    st.caption('The challenge is a teaching exercise, not a claim about the feasibility of any particular parcel.')

with build:
    st.subheader('Project economics — live results')
    a,b,c,d = st.columns(4)
    a.metric('Total apartments',f"{r['units']:,}")
    b.metric('Restricted apartments',f"{r['affordable_units']:,}",f"{r['affordable_pct']}% of homes",delta_color='off')
    c.metric('Annual net operating income',fmt(r['noi']))
    d.metric('Funding gap' if r['funding_gap']>0 else 'Modeled surplus',fmt(r['funding_gap']))
    values = pd.DataFrame({'Source or use':['Total development cost','Less: public land credit','Net development cost','Stabilized property value','Public capital subsidy','Funding gap (+) / surplus (-)'],
        'Millions ($)':[r['gross_tdc']/1e6,-r['land_credit']/1e6,r['net_tdc']/1e6,r['stabilized_value']/1e6,r['capital_subsidy']/1e6,r['funding_gap']/1e6]})
    lft,rgt=st.columns([1.2,1])
    with lft:
        st.markdown('#### Where the money comes from')
        st.bar_chart(pd.DataFrame({'$ millions':{'Net development cost':r['net_tdc']/1e6,'Value + public subsidy':(r['stabilized_value']+r['capital_subsidy'])/1e6}}),horizontal=True)
        if r['feasible_proxy']:
            st.success('Modeled value and public support meet or exceed project cost. This is NOT a financing commitment or a calculation of developer profit.')
        else:
            st.error(f"Unfunded amount: **{fmt(r['funding_gap'])}**. What policy or development change could close it?")
    with rgt:
        st.markdown('#### Operating economics')
        st.dataframe(pd.DataFrame({'Item':['Gross annual rents','Effective annual rents','Operating expenses','Annual NOI','Value at cap rate','Yield on net cost'],
            'Result':[fmt(r['gross_revenue']),fmt(r['effective_revenue']),fmt(r['effective_revenue']-r['noi']),fmt(r['noi']),fmt(r['stabilized_value']),f"{r['yield_on_cost']*100:.2f}%" if r['yield_on_cost'] is not None else 'N/A']}),hide_index=True,use_container_width=True)
        st.caption(f"Public subsidy per restricted home: {fmt(r['support_per_affordable_unit']) if r['support_per_affordable_unit'] is not None else 'N/A'}. Includes public land credit; not a measure of lifetime subsidy effectiveness.")
    st.markdown('#### Apartment mix')
    st.bar_chart(pd.DataFrame({'Homes':{'Market-rate':r['market_units'],'Income-restricted':r['affordable_units']}}),horizontal=True)
    with st.expander('How the model works — the math'):
        st.markdown('''1. **Gross rent** = 12 × [(market-rate homes × market rent) + (restricted homes × restricted rent)].
2. **Effective rent** = gross rent × (1 − vacancy/collection loss).
3. **NOI** = effective rent × (1 − operating expense ratio).
4. **Stabilized value** = NOI ÷ cap rate.
5. **Net development cost** = (homes × all-in cost per home) + incremental parking cost − public land cost credit.
6. **Funding gap** = net development cost − stabilized value − capital subsidy.

The model uses stabilized value as a simplified proxy for capital support. It does **not** calculate debt sizing, loan interest, construction period cash flows, tax credits, rent escalations, investor returns, operating subsidy, eligibility verification, or legal restrictions.''')

with policy:
    st.subheader('What would you change as mayor?')
    st.write('Experiment with a policy lever using the sidebar, or compare preset policies below. Every policy changes who benefits and what it costs.')
    rows=[]
    for name,pi in PRESETS.items():
        x=analyze(pi)
        rows.append({'Scenario':name,'Homes':x['units'],'Affordable homes':x['affordable_units'],'Public cash subsidy ($M)':x['capital_subsidy']/1e6,'Gap ($M)':round(x['funding_gap']/1e6,1)})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    st.markdown('#### How much cash subsidy would close *your* modeled gap?')
    necessary=optimal_subsidy_m(p)
    st.metric('Total estimated cash subsidy needed',f'${necessary:,.1f}M',help='The capital subsidy that would make the simple funding gap equal zero, holding all other inputs fixed.')
    st.metric('Additional cash subsidy beyond current allocation',f'${max(0,necessary-p.subsidy_m):,.1f}M')
    st.markdown('#### Debate questions')
    st.markdown('''- **More density:** Who gains and who objects when zoning permits more homes near transit?
- **Public land:** Is below-market land a real public cost even if no cash changes hands?
- **Deep affordability:** What happens when restricted rent is far below construction and operating cost?
- **Parking:** Does a parking minimum help residents or raise housing costs?
- **Preservation:** Would the same subsidy do more good preserving existing affordable homes?''')

with compare:
    st.subheader('Classroom proposals')
    st.write('Each student can save and export their scenario. For a classroom without a connected database, the instructor can collect exported CSV files and upload them below to make a shared comparison. A shared URL alone does not synchronize student sessions.')
    name=st.text_input('Student or team name',value='',placeholder='e.g., Team Transit')
    objective=st.selectbox('My top priority',['Balanced outcomes','Most affordable homes','Most total homes','Least public subsidy','Highest financial feasibility'])
    if st.button('Save my proposal',type='primary'):
        if not name.strip():
            st.error('Please enter a team name before saving.')
        else:
            row={'Team':name.strip()[:50],'Priority':objective,'Homes':r['units'],'Affordable homes':r['affordable_units'],'Market rent':r['market_rent'],'Affordable rent':r['affordable_rent'],'Total public support ($M)':round((r['capital_subsidy']+r['land_credit'])/1e6,2),'Funding gap ($M)':round(r['funding_gap']/1e6,2),'Feasibility proxy':'Meets simple test' if r['feasible_proxy'] else 'Funding gap','Saved UTC':datetime.utcnow().strftime('%Y-%m-%d %H:%M')}
            st.session_state.saved.append(row)
            st.success('Saved in this browser session. Export to keep a copy.')
    saved=st.session_state.saved
    if saved:
        st.dataframe(pd.DataFrame(saved),hide_index=True,use_container_width=True)
        st.download_button('⬇ Download saved proposals as CSV',pd.DataFrame(saved).to_csv(index=False).encode('utf-8'),'dc_housing_proposals.csv','text/csv')
    upload=st.file_uploader('Instructor: upload one or more student CSV exports',type=['csv'],accept_multiple_files=True)
    imported=[]
    for f in upload or []:
        try:
            df=pd.read_csv(f)
            expected={'Team','Homes','Affordable homes','Funding gap ($M)'}
            if not expected.issubset(df.columns):
                st.warning(f'{f.name}: skipped, missing required columns')
                continue
            imported.append(df)
        except Exception as exc:
            st.warning(f'{f.name}: cannot load ({exc})')
    if imported:
        combined=pd.concat(([pd.DataFrame(saved)] if saved else [])+imported,ignore_index=True)
        st.markdown('#### Combined class comparison')
        st.dataframe(combined,hide_index=True,use_container_width=True)
        st.bar_chart(combined.set_index('Team')[['Homes','Affordable homes']])
        st.download_button('⬇ Download combined results',combined.to_csv(index=False).encode('utf-8'),'dc_housing_class_results.csv','text/csv')
    st.caption('No persistent data store, login system, or real-time cross-device synchronization is configured. Students must export their proposals before closing the page.')

with guide:
    st.subheader('Facilitator guide — 45–60 minutes')
    st.markdown('''**0–10 min — Housing and opportunity.** Ask what housing makes possible. Relate the discussion to neighborhood access to transit, jobs, schools, and public services.

**10–20 min — The paradox.** Show that greater production does not ensure homes are affordable at every income level.

**20–35 min — Build a project.** Begin at the baseline. Increase the affordable requirement to 50%, then 100%. Ask students why the funding gap changes. Explain that affordable rents and eligibility limits are distinct concepts.

**35–50 min — Policy challenge.** Have students work individually or in teams. Demand a defense of who benefits, which constraints bind, and how public subsidy is funded.

**50–60 min — Debrief.** Compare saved proposals. End by asking: Which outcome should DC maximize—and who decides?''')
    st.markdown('#### Important qualifications')
    st.markdown('''- **All numerical defaults are hypothetical** and must not be represented as current DC rent limits, market survey data, subsidy allocations, or actual project costs.
- 'Affordable' here means **income-restricted**. The app does not calculate income eligibility or AMI schedules. Actual restrictions may vary by program, household size, unit size, and utility allowances.
- A positive simple funding gap is not a definitive finding of infeasibility; a negative gap is **not profit**. The model deliberately omits lender terms and construction finance.
- Land contributions have economic value even when no cash subsidy is paid.
- The public policy lesson is not that all projects should maximize a single metric.''')
    st.markdown('#### Optional local examples')
    st.write('Atworth (College Park, MD): transit-adjacent, 451 income-restricted apartments; an illustration of regional partnerships and location as opportunity. Livingston Place (DC): a reminder that preserving and operating affordable housing matters long after delivery.')
    st.markdown('#### Source links for policy context')
    st.markdown('''- [DC Office of Planning — Inclusionary Zoning](https://planning.dc.gov/page/inclusionary-zoning-iz-affordable-housing-program)
- [DC Department of Housing and Community Development](https://dhcd.dc.gov/)
- [Metropolitan Washington Council of Governments — Housing](https://www.mwcog.org/)
- [Streamlit Community Cloud documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)''')

st.divider()
st.caption('DC HOUSING LAB • Classroom edition v1.0 • Developed for educational use, October 2026 • Not investment, legal, or housing eligibility advice')

import io
from dataclasses import replace
import pandas as pd
import streamlit as st
from model import Inputs, NEIGHBORHOODS, PRESETS, analyze, neighborhood_inputs, income_examples
from classroom import HOUSEHOLDS, household_results, building_html, tradeoff_messages
from display_format import money, percentage, integer

st.set_page_config(page_title='DC Housing Lab | Sidwell Friends', page_icon='🏙️', layout='wide')
st.markdown('''<style>.block-container{max-width:1320px;padding-top:1.5rem}.hero{background:linear-gradient(110deg,#10283f,#176e80);border-radius:17px;padding:22px 28px;color:white;margin-bottom:16px}.hero h1{color:white;font-size:2.3rem;margin:0}.hero p{color:#dcecf1;margin:4px 0}div[data-testid="stMetric"]{background:#f2f5f8;padding:13px;border-radius:11px}</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🏙️ DC Housing Lab</h1><p>Who gets to live in the city? A real-time housing development and policy simulator.</p></div>',unsafe_allow_html=True)
st.caption('CLASSROOM EDITION v1.2.2 • All neighborhood financial inputs and AMI amounts are hypothetical teaching assumptions, NOT current market data or official rent limits.')

if 'saved' not in st.session_state: st.session_state.saved=[]
if 'neighborhood' not in st.session_state: st.session_state.neighborhood=list(NEIGHBORHOODS)[0]
if 'scenario' not in st.session_state: st.session_state.scenario=list(PRESETS)[0]

def load(name, scenario):
    p=neighborhood_inputs(name,scenario)
    for f in p.__dataclass_fields__: st.session_state['x_'+f]=getattr(p,f)

# Streamlit runs button callbacks BEFORE widgets are created on the next rerun.
# Never assign widget-owned session state after the widget is instantiated.
def apply_density_bonus():
    units = st.session_state['x_units']
    st.session_state['x_units'] = min(500, int(round(units * 1.25 / 10) * 10))

def apply_land_contribution():
    st.session_state['x_land_credit_m'] = min(30.0, st.session_state['x_land_credit_m'] + 10.0)

def apply_grant():
    st.session_state['x_grant_m'] = min(100.0, st.session_state['x_grant_m'] + 10.0)

if 'x_units' not in st.session_state: load(st.session_state.neighborhood,st.session_state.scenario)
if 'baseline_values' not in st.session_state:
    st.session_state.baseline_values=neighborhood_inputs(st.session_state.neighborhood,st.session_state.scenario)

st.sidebar.header('Choose your city')
place=st.sidebar.selectbox('Neighborhood',list(NEIGHBORHOODS),key='neighborhood')
scenario=st.sidebar.selectbox('Policy scenario',list(PRESETS),key='scenario')
st.sidebar.caption(NEIGHBORHOODS[place]['tagline'])
if st.sidebar.button('↻ Load selected neighborhood and scenario',use_container_width=True):
    load(place,scenario)
    st.session_state.baseline_values=neighborhood_inputs(place,scenario)
    st.rerun()
st.sidebar.caption('Changing selections alone preserves your custom inputs. Click Load to apply a different starting case.')

st.sidebar.subheader('1 · Housing program')
st.sidebar.slider('Apartments',50,500,step=10,key='x_units')
st.sidebar.slider('Affordable / restricted units (%)',0,100,step=5,key='x_affordable_pct')
st.sidebar.slider('Market rent ($ / month)',1500,6000,step=100,key='x_market_rent')
st.sidebar.slider('Affordable rent ($ / month)',500,3500,step=50,key='x_affordable_rent')
st.sidebar.subheader('2 · Development & policy')
st.sidebar.slider('All-in development cost per unit ($)',250000,800000,step=25000,key='x_cost_per_unit')
st.sidebar.slider('Public grant ($M)',0.0,100.0,step=1.0,key='x_grant_m')
st.sidebar.slider('Public land discount ($M)',0.0,30.0,step=1.0,key='x_land_credit_m')
st.sidebar.slider('Repayable public loan ($M)',0.0,50.0,step=1.0,key='x_loan_m')
with st.sidebar.expander('Advanced financial assumptions'):
    st.slider('Vacancy / bad debt (%)',0.0,20.0,step=1.0,key='x_vacancy_pct')
    st.slider('Operating expenses (% of effective rent)',20.0,65.0,step=1.0,key='x_opex_pct')
    st.slider('Cap rate (%)',3.0,9.0,step=0.25,key='x_cap_rate_pct')
    st.slider('Public loan interest rate (%)',0.0,10.0,step=0.5,key='x_loan_rate_pct')
    st.slider('Public loan term (years)',10,40,step=5,key='x_loan_years')
    st.slider('Required value-over-cost margin (%)',0.0,25.0,step=1.0,key='x_return_margin_pct')
    st.slider('Incremental parking cost per apartment ($)',0,50000,step=5000,key='x_extra_parking_per_unit')

p=Inputs(**{f:st.session_state['x_'+f] for f in Inputs.__dataclass_fields__})
r=analyze(p)
fm=lambda x:money(x, compact=True)

tabs=st.tabs(['🎓 Instructor view','🏗️ Build a project','🏛️ Policy lab','👨‍👩‍👧‍👦 Who can afford it?','🏆 Classroom challenge','📖 Model & teaching notes'])
with tabs[0]:
    st.subheader(f'Your development: {place}')
    a,b,c,d=st.columns(4)
    a.metric('Homes',integer(r['units'])); b.metric('Restricted homes',integer(r['restricted_units']));c.metric('Public grant',fm(r['grant']));d.metric('Gap to required margin',fm(r['margin_gap']) if r['margin_gap']>0 else 'None',help='Positive = remaining gap; zero or negative = meets this simplified margin test. This is not a financeability approval.')
    st.caption(f"Restricted share: {percentage(100*r['restricted_units']/r['units'], 1)} of all homes; market-rate share: {percentage(100*r['market_units']/r['units'], 1)}.")
    st.markdown('### See your housing mix')
    st.markdown('''<style>.building{background:#eef4f7;border-radius:14px;padding:20px;margin:8px 0 18px;color:#20364a}.legend{display:flex;gap:20px;font-size:14px;font-weight:650;margin-bottom:12px}.legend span:first-child{color:#087f8c}.legend span:last-child{color:#52677c}.windows{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:5px;max-width:720px}.apt{display:block;height:18px;border-radius:3px}.apt.aff{background:#087f8c}.apt.mkt{background:#8ca8ba}.building .caption{font-size:12px;color:#334b5e;margin-top:10px}</style>''',unsafe_allow_html=True)
    st.markdown(building_html(r['units'],r['restricted_units']),unsafe_allow_html=True)
    st.caption('A stylized representation of unit mix only—not actual height, floor area, zoning, or a building design.')
    st.markdown('### What changed and why?')
    for message in tradeoff_messages(p,st.session_state.baseline_values):st.info(message)
    st.markdown('### Three quick experiments')
    st.write('**1. Raise affordability to 80%.** Why do revenue and value change? **2. Raise allowable density.** Does it always help? **3. Add a grant, then replace it with a repayable loan.** Why are the outcomes different?')
    if r['meets_simple_test']:st.success('✓ The modeled value covers cost plus the illustrative required margin. Not a financing approval.')
    else: st.warning('The project does not reach the illustrative required margin. Try changing the plan or policy.')
    st.write('**Ask:** Is it more equitable to build fewer deeply affordable units in a high-opportunity neighborhood, or more units elsewhere?')
    st.info('Instructor tip: students should distinguish a public grant (permanent capital support), discounted land (foregone public value), and a repayable loan (a financial obligation).')

with tabs[1]:
    st.subheader('Live project economics')
    a,b,c,d=st.columns(4)
    a.metric('Annual NOI',fm(r['noi']));b.metric('Stabilized value',fm(r['stabilized_value']));c.metric('Net development cost',fm(r['net_cost']));d.metric('Value after public-loan payments',fm(r['residual_value']))
    st.caption('The after-loan value is a classroom proxy: it capitalizes NOI net of annual loan repayment at the same cap rate; it is not a full debt/equity valuation.')
    plot=pd.DataFrame({'Millions ($)':{'Net project cost':r['net_cost']/1e6,'Capitalized NOI after public-loan service + grant':(r['residual_value']+r['grant'])/1e6,'Target (cost + required margin)':r['net_cost']*(1+p.return_margin_pct/100)/1e6}})
    st.bar_chart(plot,horizontal=True)
    st.dataframe(pd.DataFrame([('Gross scheduled rent',r['gross_rent']),('Effective rent',r['egi']),('Operating expenses',r['egi']-r['noi']),('NOI',r['noi']),('Annual public-loan payment',r['annual_public_loan_payment']),('NOI net of public-loan payment',r['residual_noi']),('Project cost net of land contribution',r['net_cost']),('Cash grant',r['grant']),('Loan proceeds (repayable, NOT grant)',r['loan']),('Basic gap before return margin',r['basic_gap']),('Gap to required margin',r['margin_gap'])],columns=['Measure','Amount ($)']).style.format({'Amount ($)':lambda x: money(x)}),hide_index=True,use_container_width=True)
    if r['residual_noi']<=0:st.error('Public loan payment consumes all modeled NOI. This loan is not supportable under the simplified test.')
    st.caption('Cash grant does not create operating income. Repayable public loan may provide upfront cash but also requires future debt service. Private construction and permanent loans are not modeled.')

with tabs[2]:
    st.subheader('Three public policy levers')
    st.write('Use the sidebar to change each intervention, or use the buttons below to apply the policies directly.')
    x,y,z=st.columns(3)
    with x:
        st.markdown('**Density bonus: +25% homes**')
        st.caption('Increases homes and development cost; assumes rents/cost per unit do not change.')
        st.button('Apply density bonus',use_container_width=True,on_click=apply_density_bonus)
    with y:
        st.markdown('**Public land contribution: +$10M**')
        st.caption('Reduces net development cost; the land has a real public opportunity cost.')
        st.button('Apply land contribution',use_container_width=True,on_click=apply_land_contribution)
    with z:
        st.markdown('**Public grant: +$10M**')
        st.caption('Closes a gap through permanent cash support, subject to budget capacity.')
        st.button('Apply grant',use_container_width=True,on_click=apply_grant)
    st.divider()
    st.markdown('#### What if the city offers a loan instead?')
    st.write(f"Current public loan: **{fm(r['loan'])}**; annual payment: **{fm(r['annual_public_loan_payment'])}**. Loan coverage from total NOI: **{r['ds_coverage']:.2f}×**." if r['ds_coverage'] is not None else 'No repayable public loan selected.')
    st.caption('Loan proceeds are not added to grant proceeds for the valuation-based feasibility test. The loan payment reduces residual NOI; loan principal cannot also be deducted from value without double counting.')
    st.markdown('#### Compare neighborhood baselines (illustrative)')
    rows=[]
    for name in NEIGHBORHOODS:
        x=analyze(neighborhood_inputs(name,scenario))
        rows.append({'Neighborhood':name,'Homes':x['units'],'Restricted':x['restricted_units'],'Market rent ($/mo)':x['market_rent'],'Cost per home ($)':x['cost_per_unit'],'Gap to margin ($M)':round(x['margin_gap']/1e6,1)})
    st.dataframe(pd.DataFrame(rows).style.format({'Homes':'{:,.0f}','Restricted':'{:,.0f}','Market rent ($/mo)':lambda x:money(x),'Cost per home ($)':lambda x:money(x),'Gap to margin ($M)':lambda x: money(x*1e6,compact=True)}),hide_index=True,use_container_width=True)

with tabs[3]:
    st.subheader('What does “affordable” actually mean?')
    st.write('A restricted apartment is not necessarily affordable to every household. Compare an illustrative income level with the actual modeled rent.')
    assumed_ami=st.number_input('Hypothetical annual AMI baseline for this exercise ($, four-person household)',min_value=40000,max_value=300000,value=160000,step=5000)
    st.caption('This is a classroom-only income benchmark. Actual HUD/DC limits differ by fiscal year and household size; this tool does NOT determine eligibility or rent limits.')
    rows=[]
    for x in income_examples(assumed_ami):
        rows.append({'Income tier':x['label'],'Gross annual income ($)':round(x['income']),'30% monthly housing budget ($)':round(x['rent_budget']),'Affordable model rent within budget?':'Yes' if p.affordable_rent<=x['rent_budget'] else 'No'})
    st.dataframe(pd.DataFrame(rows).style.format({'Gross annual income ($)':lambda x: money(x), '30% monthly housing budget ($)':lambda x: money(x)}),hide_index=True,use_container_width=True)
    st.metric('Modeled restricted rent',f'${p.affordable_rent:,}/month')
    st.markdown('### Four households: could they live here?')
    utility=st.slider('Estimated monthly utilities paid by tenant ($)',0,400,150,25,key='utilities')
    profiles=household_results(p,utility_allowance=utility)
    profile_df=pd.DataFrame(profiles).drop(columns=['Story'])
    st.dataframe(profile_df.style.format({c: (lambda x: money(x)) for c in profile_df.columns if '($' in c}).format({'Household size':'{:,.0f}'}),hide_index=True,use_container_width=True)
    st.caption('All household incomes are fictional examples, not typical wages or verified occupation-level pay in DC. The budget is 30% of gross income INCLUDING the illustrated utility allowance. Ability to pay is not the same as eligibility or availability.')
    affordable_count=sum(x['Can afford restricted rent?']=='Yes' for x in profiles)
    st.info(f'{affordable_count} of 4 illustrative households can afford the modeled restricted rent under these assumptions. A Yes does not indicate they qualify for a restricted apartment.')
    st.warning('Rent budget is shown before utilities. AMI percentages in this exercise are not program-qualified affordable rent schedules. Actual programs apply different formulas and compliance rules.')
    st.markdown('**Ask students:** Who is left out when a building is restricted to households at 80% AMI, but rents are too high for families at 30% AMI?')

with tabs[4]:
    st.subheader('10-minute housing policy challenge')
    st.write('Goal: create ≥200 homes including ≥60 restricted homes, with no modeled return-margin gap. Then defend total public support and the rents households will pay.')
    goals=[p.units>=200,r['restricted_units']>=60,r['meets_simple_test']]
    st.progress(sum(goals)/3,text=f'{sum(goals)} of 3 goals met')
    for passed,label in zip(goals,['At least 200 total homes','At least 60 restricted homes','Target cost + margin is covered']):
        st.write(('✅ ' if passed else '⬜ ')+label)
    team=st.text_input('Team name',placeholder='Team Metro')
    priority=st.selectbox('Most important policy outcome',['More homes','Deeper affordability','Lower public cost','Financial feasibility','Balanced access'])
    if st.button('Save proposal',type='primary'):
        if not team.strip():st.error('Enter your team name first.')
        else:
            st.session_state.saved.append({'Team':team.strip()[:40],'Neighborhood':place,'Priority':priority,'Homes':p.units,'Restricted homes':r['restricted_units'],'Restricted rent ($)':p.affordable_rent,'Grant ($M)':p.grant_m,'Land credit ($M)':p.land_credit_m,'Loan ($M)':p.loan_m,'Margin gap ($M)':round(r['margin_gap']/1e6,2),'Goals met':sum(goals)})
            st.success('Saved to this browser session. Download a CSV to retain it.')
    if st.session_state.saved:
        df=pd.DataFrame(st.session_state.saved)
        st.dataframe(df.style.format({c:(lambda x:money(x*1e6,compact=True)) for c in df.columns if '($M)' in c}).format({c:lambda x: money(x) for c in df.columns if '($)' in c}).format({c:'{:,.0f}' for c in ['Homes','Restricted homes'] if c in df.columns}),hide_index=True,use_container_width=True)
        st.download_button('Download proposal(s) CSV',df.to_csv(index=False),'dc_housing_proposals_v1_2.csv','text/csv')
    files=st.file_uploader('Instructor: combine student exports here',type=['csv'],accept_multiple_files=True)
    loaded=[]
    for file in files or []:
        try:
            x=pd.read_csv(file)
            if {'Team','Homes','Restricted homes','Margin gap ($M)'}.issubset(x.columns):loaded.append(x)
            else:st.warning(f'{file.name}: does not match proposal format')
        except Exception as exc:st.warning(f'{file.name}: could not open ({exc})')
    if loaded:
        combined=pd.concat(([pd.DataFrame(st.session_state.saved)] if st.session_state.saved else [])+loaded,ignore_index=True)
        st.dataframe(combined.style.format({c:(lambda x:money(x*1e6,compact=True)) for c in combined.columns if '($M)' in c}).format({c:lambda x:money(x) for c in combined.columns if '($)' in c}).format({c:'{:,.0f}' for c in ['Homes','Restricted homes'] if c in combined.columns}),hide_index=True,use_container_width=True)
        st.bar_chart(combined.set_index('Team')[['Homes','Restricted homes']])
        st.download_button('Download combined class results',combined.to_csv(index=False),'class_results.csv','text/csv')
    st.caption('No live multi-user synchronization or database. Student files must be shared with the instructor for aggregation.')

with tabs[5]:
    st.subheader('Teaching plan: 60 minutes')
    st.markdown('''**0–10:** Who gets access to good neighborhoods? Discuss housing, schools, jobs, and transit.  
**10–20:** Pick Friendship Heights versus Congress Heights. Why can both be hard to build in?  
**20–35:** Adjust affordability, rent, and density. Walk through NOI and the gap.  
**35–50:** Student teams choose a policy intervention and save their own plan.  
**50–60:** Compare trade-offs, affordability at different incomes, and what constitutes a good city.''')
    st.markdown('### Model integrity and limits')
    st.markdown('''- Illustrative rents, costs, zoning capacity, subsidies, and AMI baseline; **not current DC facts or official limits**.
- Gross rent → less vacancy/bad debt → less operating expenses → NOI → NOI / cap rate.
- A grant is permanent cash capital. A public land discount reduces the cost basis in this exercise, but uses a valuable public asset.
- A repayable public loan is modeled with amortizing annual payments; capitalized residual NOI is used as a simplified proxy for its burden. Loan proceeds are **not** treated as a permanent subsidy.
- Required margin compares residual capitalized value plus grants against land-adjusted cost plus a classroom return buffer. It is **not an investor IRR, developer fee, financing commitment, tax-credit model, or debt-sizing exercise**.
- Increasing units assumes scalable costs; real zoning, parcels, land value, site constraints, infrastructure and entitlement approvals can prevent that outcome.
- Actual restricted rents depend on the program, AMI vintage, household/unit sizing, and allowances. The illustration cannot establish legal eligibility.
- A project can satisfy this simplified mathematical test while still being impossible to finance; likewise a project that fails it may be possible with other sources of capital.''')
    st.markdown('Relevant official resources: [DC Office of Planning](https://planning.dc.gov/) · [DC DHCD](https://dhcd.dc.gov/) · [HUD income limits](https://www.huduser.gov/portal/datasets/il.html).')
st.divider();st.caption('DC Housing Lab v1.2.2 • October 2026 • Illustrative classroom tool; not investment, legal or eligibility advice.')

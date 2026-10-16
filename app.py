import io
from dataclasses import replace
import pandas as pd
import streamlit as st
from model import Inputs, NEIGHBORHOODS, PRESETS, analyze, neighborhood_inputs, income_examples
from classroom import HOUSEHOLDS, household_results, building_html, tradeoff_messages
from display_format import money, percentage, integer
from upgrade import SHOCKS, shock, sensitivity, minimum_grant_to_margin, snapshot
from capital_stack import breakdown, visual
from cash_flow import annual_waterfall, waterfall_html
from visuals import CSS, building_massing, finance_stack, waterfall_chart
from neighborhood_map import render_map, nearest_neighborhood
from student_report import create_student_pdf
from forecast import ForecastAssumptions, project
from public_policy import PublicPolicyAssumptions, evaluate
from evidence import planning_area_context, district_production, records as evidence_sources
from live_data import fetch_gis, fetch_acs, census_key, DataUnavailable, GIS_LAYER, ACS_BASE

st.set_page_config(page_title='DC Housing Lab | Sidwell Friends', page_icon='🏙️', layout='wide')
st.markdown(CSS,unsafe_allow_html=True)
st.markdown('<div class="hero-v14"><div class="eyebrow">URBAN PLANNING / AFFORDABLE HOUSING</div><h1>DC Housing Lab</h1><p>Build a neighborhood. Finance the housing. See who can afford to live there.</p></div>',unsafe_allow_html=True)
st.caption('CLASSROOM EDITION v1.9.3 • Historical DC government evidence is separate from illustrative development assumptions.')

if 'saved' not in st.session_state: st.session_state.saved=[]
if 'comparison' not in st.session_state: st.session_state.comparison={}
if 'neighborhood' not in st.session_state: st.session_state.neighborhood=list(NEIGHBORHOODS)[0]
if 'scenario' not in st.session_state: st.session_state.scenario=list(PRESETS)[0]

def load(name, scenario):
    p=neighborhood_inputs(name,scenario)
    for f in p.__dataclass_fields__: st.session_state['x_'+f]=getattr(p,f)

# Streamlit runs button callbacks BEFORE widgets are created on the next rerun.
# Never assign widget-owned session state after the widget is instantiated.
def reset_case():
    load(st.session_state.neighborhood,st.session_state.scenario)
    st.session_state.baseline_values=neighborhood_inputs(st.session_state.neighborhood,st.session_state.scenario)
    st.session_state.comparison={}
    st.session_state.pop('latest_shock',None)

def apply_density_bonus():
    units = st.session_state['x_units']
    st.session_state['x_units'] = min(500, int(round(units * 1.25 / 10) * 10))

def apply_land_contribution():
    st.session_state['x_land_credit_m'] = min(30.0, st.session_state['x_land_credit_m'] + 10.0)

def apply_grant():
    st.session_state['x_grant_m'] = min(100.0, st.session_state['x_grant_m'] + 10.0)

def apply_shock():
    current=Inputs(**{f:st.session_state['x_'+f] for f in Inputs.__dataclass_fields__})
    after=shock(current,st.session_state['shock_choice'])
    for field in Inputs.__dataclass_fields__:
        st.session_state['x_'+field]=getattr(after,field)
    st.session_state['latest_shock']=st.session_state['shock_choice']

# Map interactions set a pending choice, applied BEFORE the sidebar selectbox is created.
if st.session_state.get('pending_map_neighborhood'):
    new_place=st.session_state.pop('pending_map_neighborhood')
    st.session_state['neighborhood']=new_place
    load(new_place,st.session_state.scenario)
    st.session_state.baseline_values=neighborhood_inputs(new_place,st.session_state.scenario)
if 'x_units' not in st.session_state: load(st.session_state.neighborhood,st.session_state.scenario)
# Backfill new fields for users whose Streamlit session was created on v1.3.
for field in Inputs.__dataclass_fields__:
    if 'x_'+field not in st.session_state:
        st.session_state['x_'+field]=getattr(Inputs(),field)
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
st.sidebar.button('Reset project inputs to selected baseline',on_click=reset_case,use_container_width=True)

st.sidebar.subheader('Reality Check')
st.sidebar.selectbox('Unexpected development event',list(SHOCKS),key='shock_choice')
st.sidebar.button('Apply Reality Check',on_click=apply_shock,use_container_width=True)
if 'latest_shock' in st.session_state:st.sidebar.caption('Last applied: '+st.session_state['latest_shock'])
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
    st.slider('Illustrative committed private debt ($M)',0.0,100.0,step=1.0,key='x_private_debt_m')
    st.markdown('**Private permanent loan sizing**')
    st.slider('Private loan interest rate (%)',0.0,12.0,step=0.25,key='x_private_rate_pct')
    st.slider('Private loan amortization (years)',10,40,step=5,key='x_private_amort_years')
    st.slider('Minimum total DSCR (×)',1.0,2.0,step=0.05,key='x_min_total_dscr')
    st.slider('Maximum private loan LTV (%)',0.0,85.0,step=5.0,key='x_max_private_ltv_pct')
    st.slider('Maximum private loan LTC (%)',0.0,90.0,step=5.0,key='x_max_private_ltc_pct')
    st.slider('Illustrative committed equity ($M)',0.0,100.0,step=1.0,key='x_committed_equity_m')

p=Inputs(**{f:st.session_state['x_'+f] for f in Inputs.__dataclass_fields__})
r=analyze(p)
fm=lambda x:money(x, compact=True)

presentation=st.toggle('Presentation mode · projector layout',value=False,key='presentation_mode')
if presentation:
    st.markdown("""<style>
      section[data-testid="stSidebar"]{display:none!important}
      [data-testid="stAppViewContainer"] .main .block-container{max-width:1500px!important;padding-top:1rem!important}
      div[data-testid="stTabs"] button[role="tab"]{font-size:1.06rem!important}
      .hero-v14{padding:12px 22px!important}
      .hero-v14 h1{font-size:2.65rem!important}
      [data-testid="stMetricValue"]{font-size:2.1rem!important}
    </style>""",unsafe_allow_html=True)
    st.caption('Projector tip: press F11 in your browser for true full-screen; toggle this switch off to restore inputs.')
tabs=st.tabs(['🎓 Instructor view','🏗️ Build a project','🏛️ Policy lab','👨‍👩‍👧‍👦 Who can afford it?','🏆 Classroom challenge','📊 Stress test & compare','📖 Model & teaching notes','📈 Ten-year outlook','🏛️ Public subsidy efficiency'])
with tabs[0]:
    st.subheader(f'Your development: {place}')
    a,b,c,d=st.columns(4)
    a.metric('Homes',integer(r['units'])); b.metric('Restricted homes',integer(r['restricted_units']));c.metric('Public grant',fm(r['grant']));d.metric('Economic margin gap',fm(r['margin_gap']) if r['margin_gap']>0 else 'None',help='Positive = remaining gap; zero or negative = meets this simplified margin test. This is not a financeability approval.')
    st.caption(f"Restricted share: {percentage(100*r['restricted_units']/r['units'], 1)} of all homes; market-rate share: {percentage(100*r['market_units']/r['units'], 1)}.")
    st.markdown(building_massing(r['units'],r['restricted_units']),unsafe_allow_html=True)
    if presentation:
        st.markdown('### Can we finance and operate it?')
        st.markdown(finance_stack(breakdown(r),lambda v:money(v,compact=True)),unsafe_allow_html=True)
        st.markdown(waterfall_chart(annual_waterfall(r),lambda v:money(v,compact=True)),unsafe_allow_html=True)
        st.caption('Projection mode simplifies the presentation; technical detail remains in Build a project.')
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
    st.markdown('### Sources & uses | capital stack')
    stack=breakdown(r)
    st.markdown(finance_stack(stack,lambda v:money(v,compact=True)),unsafe_allow_html=True)
    f1,f2,f3=st.columns(3)
    f1.metric('Net development uses',fm(stack['cost']))
    f2.metric('Identified funding sources',fm(stack['available_total']))
    f3.metric('Additional equity needed',fm(stack['shortfall']))
    st.caption('Includes only the supportable private loan actually modeled, not the requested loan above lender limits. Red indicates the remaining amount to be raised. Bars use the same dollar scale.')
    if stack['unused_sources']>0.01:
        st.warning(f"Identified sources exceed uses by {fm(stack['unused_sources'])}. This is excess proposed funding, not profit. The sources bar includes that excess.")
    source_table=pd.DataFrame([{'Capital source':label,'Available ($)':amount,'Applied to uses ($)':dict(stack['allocated']).get(label,0.0)} for label,amount in stack['sources']] + [{'Capital source':'Additional equity required','Available ($)':0.0,'Applied to uses ($)':stack['shortfall']}])
    st.dataframe(source_table.style.format({'Available ($)':money,'Applied to uses ($)':money}),hide_index=True,use_container_width=True)
    csv_export=source_table.to_csv(index=False).encode('utf-8')
    st.download_button('Download capital stack (CSV)',data=csv_export,file_name='dc_housing_lab_capital_stack.csv',mime='text/csv',key='download_capital_stack')
    st.caption('Sources-and-uses is a funding check, not an appraisal or investment return. The land contribution reduces net project cost. Private loans are subject to the simplified debt-capacity tests; public loans are assumed available but must be repaid. Overfunded sources are disclosed, not interpreted as equity profits.')
    st.markdown('### Annual operating cash-flow waterfall')
    st.caption('Illustrative **stabilized annual** operations at the current rent and operating assumptions. This is one representative year, not a multi-year cash-flow forecast.')
    cf=annual_waterfall(r)
    st.markdown(waterfall_chart(cf,lambda v:money(v,compact=True)),unsafe_allow_html=True)
    wc1,wc2,wc3,wc4=st.columns(4)
    wc1.metric('Annual NOI (before debt)',fm(cf['noi']))
    wc2.metric('Total annual debt service',fm(cf['total_ds']))
    wc3.metric('Annual cash flow to equity',fm(cf['cash_to_equity']))
    wc4.metric('Cash-on-cash on required equity',f"{cf['cash_on_cash_pct']:.1f}%" if cf['cash_on_cash_pct'] is not None else 'N/A')
    st.caption('Cash-on-cash = cash flow after modeled public and private debt service ÷ **total equity required** by the capital stack, not entered committed equity. Negative values are operating cash deficits. This is not IRR, total return, or a distribution forecast.')
    if cf['equity_gap']>0.01:
        st.warning(f"The capital stack still needs {fm(cf['equity_gap'])} additional equity; the cash-on-cash ratio assumes this full equity is raised. It does NOT mean a cash distribution is available to existing investors.")
    if not cf['coverage_pass']:
        st.error('Combined public and private debt payments fail the selected minimum DSCR. The modeled cash flow may be unsustainable even if it is positive.')
    if cf['cash_to_equity']<0:
        st.error('Modeled operations have negative cash flow after debt service: additional support or restructuring would be needed.')
    if cf['equity_required']<=0:
        st.info('No positive modeled equity requirement; cash-on-cash is not meaningful and is shown as N/A.')
    cf_table=pd.DataFrame([{'Annual cash-flow line':label,'Amount ($/year)':amount} for label,amount in cf['rows']])
    st.dataframe(cf_table.style.format({'Amount ($/year)':money}),hide_index=True,use_container_width=True)
    st.download_button('Download annual cash-flow waterfall (CSV)',cf_table.to_csv(index=False).encode('utf-8'),file_name='dc_housing_lab_annual_cash_flow.csv',mime='text/csv',key='download_cash_flow')
    with st.expander('What this waterfall includes and excludes'):
        st.markdown('**Scheduled rent → collection/vacancy loss → operating expenses → NOI → public debt service → private debt service → annual cash flow to equity.** Loan proceeds, grants and equity are financing sources, **not annual rental income**. Debt payments are below NOI and therefore do not affect unlevered property value. The illustration excludes replacement reserves, capital expenditures, construction-period carry, income taxes, fees, depreciation, refinancing and sale proceeds; it assumes the loan terms are outstanding for the representative stabilized year. Actual distributable cash may be lower. The public loan is not independently capped by DSCR; a warning is shown if combined coverage fails.')

    st.markdown('### Private permanent loan and required equity')
    k1,k2,k3,k4=st.columns(4)
    k1.metric('Maximum supportable private loan',fm(r['private_debt_capacity']))
    k2.metric('Modeled private loan used',fm(r['funded_private_debt']))
    k3.metric('Required equity',fm(r['equity_required']))
    k4.metric('Total DSCR',f"{r['total_dscr']:.2f}×" if r['total_dscr'] is not None else 'N/A')
    st.caption('Private borrowing = lower of entered commitment and the most restrictive DSCR, LTV and LTC limits. All public debt payments are included in total DSCR. No modeled debt means DSCR is N/A.')
    limits=pd.DataFrame([
        {'Sizing constraint':'Total DSCR','Maximum private debt ($)':r['private_debt_by_dscr']},
        {'Sizing constraint':'Loan-to-value (LTV)','Maximum private debt ($)':r['private_debt_by_ltv']},
        {'Sizing constraint':'Loan-to-cost (LTC)','Maximum private debt ($)':r['private_debt_by_ltc']},
        {'Sizing constraint':'Requested private debt','Maximum private debt ($)':r['private_debt']}])
    st.dataframe(limits.style.format({'Maximum private debt ($)':money}),hide_index=True,use_container_width=True)
    if r['private_debt_shortfall']>0.01:
        st.warning(f"Entered private debt exceeds sizing capacity by {fm(r['private_debt_shortfall'])}. Binding limit(s): {r['binding_private_limits']}.")
    if r['additional_equity_needed']>0.01:
        st.error(f"Additional equity needed beyond entered commitment: {fm(r['additional_equity_needed'])}.")
    else: st.success('Entered equity commitment covers the simplified remaining equity requirement.')
    if r['total_annual_debt_service']>0 and r['total_dscr']<p.min_total_dscr-1e-9:
        st.error('Total debt service does not meet the selected minimum coverage; the public loan alone may exceed debt-service capacity.')
    st.caption('Private-loan proceeds are modeled at the entered commitment up to supportable capacity. Real lenders also test reserves, cash flow, loan maturity, guarantees, and other restrictions.')
    a,b,c,d=st.columns(4)
    a.metric('Annual NOI',fm(r['noi']));b.metric('Stabilized value',fm(r['stabilized_value']));c.metric('Net development cost',fm(r['net_cost']));d.metric('Capital funding gap',fm(r['capital_stack_gap']))
    st.caption('Property value capitalizes unlevered NOI before debt service. Economic margin gap and capital funding gap are different tests. Negative gaps indicate surpluses.')
    st.markdown('### Grant vs. repayable loan: same upfront dollars, different economics')
    demo_m=st.slider('Compare equal grant and public loan amounts ($M)',0,30,10,5,key='grant_loan_demo')
    from dataclasses import replace as _replace
    grant_case=analyze(_replace(p,grant_m=p.grant_m+demo_m,loan_m=p.loan_m))
    loan_case=analyze(_replace(p,grant_m=p.grant_m,loan_m=p.loan_m+demo_m))
    demo=pd.DataFrame([{'Case':'Additional grant','Upfront public capital ($)':demo_m*1e6,'Economic margin gap ($)':grant_case['economic_gap'],'Capital funding gap ($)':grant_case['capital_stack_gap'],'Annual public-loan payment ($)':grant_case['annual_public_loan_payment']},{'Case':'Additional loan','Upfront public capital ($)':demo_m*1e6,'Economic margin gap ($)':loan_case['economic_gap'],'Capital funding gap ($)':loan_case['capital_stack_gap'],'Annual public-loan payment ($)':loan_case['annual_public_loan_payment']}])
    st.dataframe(demo.style.format({c:lambda v: money(v) for c in demo.columns if '($)' in c}),hide_index=True,use_container_width=True)
    st.caption('Scenarios add funding to the currently selected base case. Both supply upfront capital; only the loan requires repayment. No private-debt interest costs, covenant restrictions or grant eligibility tests are modeled.')
    plot=pd.DataFrame({'Millions ($)':{'Net project cost':r['net_cost']/1e6,'Unlevered stabilized value + grant':(r['stabilized_value']+r['grant'])/1e6,'Target (cost + required margin)':r['net_cost']*(1+p.return_margin_pct/100)/1e6}})
    st.bar_chart(plot,horizontal=True)
    st.dataframe(pd.DataFrame([('Gross scheduled rent',r['gross_rent']),('Effective rent',r['egi']),('Operating expenses',r['egi']-r['noi']),('NOI',r['noi']),('Annual public-loan payment',r['annual_public_loan_payment']),('NOI net of public-loan payment',r['residual_noi']),('Project cost net of land contribution',r['net_cost']),('Cash grant',r['grant']),('Loan proceeds (repayable, NOT grant)',r['loan']),('Requested private loan',r['private_debt']),('Supportable private loan used',r['funded_private_debt']),('Private debt service / year',r['private_annual_debt_service']),('Total public + private debt service / year',r['total_annual_debt_service']),('Equity required after supportable private loan',r['equity_required']),('Additional equity needed beyond commitment',r['additional_equity_needed']),('Illustrative equity commitments',r['committed_equity']),('Capital funding gap (sources less uses)',r['capital_stack_gap']),('Economic gap before margin',r['basic_gap']),('Economic gap to required margin',r['margin_gap'])],columns=['Measure','Amount ($)']).style.format({'Amount ($)':lambda x: money(x)}),hide_index=True,use_container_width=True)
    if r['residual_noi']<=0:st.error('Public loan payment consumes all modeled NOI; public-only DSCR is below 1.0x.')
    if r['public_loan_dscr'] is not None: st.metric('Public loan DSCR (excludes private debt)',f"{r['public_loan_dscr']:.2f}×")
    st.info('Legacy committed-sources capital gap = net development cost − grants − public loan proceeds − illustrative committed private debt − illustrative committed equity. Positive indicates unfilled funding; negative indicates excess identified sources. The new debt sizing and equity analysis above uses supportable rather than simply entered debt.')
    st.caption('Cash grant does not create operating income. Repayable public loan may provide upfront cash but also requires future debt service. Private debt and equity commitments are illustrative sources, not sized from actual lender or investor commitments. Private loan DSCR, LTV and LTC limits are illustrative; they do not represent a lender commitment.')

with tabs[2]:
    st.subheader('Explore DC neighborhoods on the map')
    st.caption('Click one of the neighborhood markers to load its illustrative development baseline. Map points represent approximate neighborhood centers, not parcel locations. Map tiles use OpenStreetMap without an API key; internet access is required.')
    map_event=None
    if st.checkbox('Display online interactive map (requires external map tiles)',value=True,key='display_online_map'):
        try:
            map_event=render_map(place)
        except Exception:
            st.warning('Map service unavailable. Use the neighborhood dropdown in the sidebar; all financial controls still work.')
    st.caption('Fallback: choose a neighborhood from the sidebar and click Load selected neighborhood and scenario. No map API key is necessary for the model.')
    clicked=nearest_neighborhood((map_event or {}).get('last_object_clicked'))
    if clicked and clicked != place:
        st.session_state['pending_map_neighborhood']=clicked
        st.rerun()
    st.caption('The map is geographic context only. Rents, costs, density and zoning assumptions are educational scenarios, NOT verified neighborhood-level market or zoning data.')
    st.divider()
    st.subheader('DC evidence desk | historical government figures')
    dc = district_production()
    ctx = planning_area_context(place)
    st.caption('These are government-reported historical observations for DC planning areas, NOT neighborhood-level rents, current affordable inventory, site zoning, or underwriting inputs. Planning-area boundaries differ from ward and neighborhood boundaries.')
    c1,c2,c3=st.columns(3)
    c1.metric('Districtwide homes delivered through Jul 2024',f"{dc['delivered_units']:,}",help='DMPED announcement dated July 29, 2024; not a current 2026 total.')
    c2.metric(f"{ctx['area']} dedicated affordable units (2018)",f"{ctx['existing_2018']:,}",help='2018 planning-area inventory from 2019 Housing Equity Report; not current count.')
    c3.metric(f"{ctx['area']} additional affordable-unit goal (2025)",f"{ctx['target_2025']:,}",help='Target from 2019 report, not achieved production.')
    st.markdown(f"**Selected neighborhood:** {place}  |  **Context geography:** {ctx['area']} planning area")
    st.info('Do not subtract the 2018 inventory from the 2025 target: the former is a stock of existing homes and the latter is a goal for additional affordable homes. Neither is the number of currently available apartments.')
    st.markdown(f"[2019 Housing Equity Report]({ctx['source_url']}) · [July 2024 production announcement]({dc['source_url']})")
    st.markdown('#### Compare historical planning-area context')
    dc_rows=[]
    for neighborhood in NEIGHBORHOODS:
        item=planning_area_context(neighborhood)
        dc_rows.append({'Neighborhood (reference point)':neighborhood,'DC planning area':item['area'],'Existing affordable units (2018)':item['existing_2018'],'Goal for additional units by 2025 (set 2019)':item['target_2025']})
    st.dataframe(pd.DataFrame(dc_rows).style.format({'Existing affordable units (2018)':'{:,.0f}','Goal for additional units by 2025 (set 2019)':'{:,.0f}'}),hide_index=True,use_container_width=True)
    with st.expander('Source register, observation periods and live-data links'):
        st.dataframe(pd.DataFrame(evidence_sources()),hide_index=True,use_container_width=True)
        st.caption('Links open official agency pages. Source dates are different; no live API results are represented as verified 2026 values.')
        st.download_button('Download evidence source register (CSV)',pd.DataFrame(evidence_sources()).to_csv(index=False).encode('utf-8'),file_name='DC_Housing_Lab_v1.9_Source_Register.csv',mime='text/csv')
    st.divider()
    st.subheader('Live DC neighborhood evidence | optional public APIs')
    st.caption('Live observations do NOT change rents, site costs, allowable density, or any development underwriting assumptions. DC GIS counts projects in the DC planning area, not the selected neighborhood. ACS data represent one tract containing the neighborhood map marker, not the entire neighborhood.')
    if st.button('Refresh public data now',key='refresh_public_data'):
        st.cache_data.clear()
        st.session_state['data_refresh_requested']=True
    @st.cache_data(ttl=86400,show_spinner=False)
    def cached_gis(name):
        return fetch_gis(name)
    @st.cache_data(ttl=86400,show_spinner=False)
    def cached_acs(name,key):
        return fetch_acs(name,key)
    try:
        g=cached_gis(place)
        st.success(f"DC GIS: {g['status']} | retrieved {g['retrieved_at']} | {g['area']} planning area")
        g1,g2,g3=st.columns(3)
        g1.metric('Projects in public GIS layer',f"{g['metrics']['project_count']:,}")
        g2.metric('Sum of reported affordable units',f"{g['metrics']['reported_unit_sum']:,}")
        g3.metric('Projects missing unit counts',f"{g['metrics']['missing_units_rows']:,}")
        st.caption('Layer covers projects started or completed since January 2015; it is NOT a current inventory, occupied unit count, net increase, or construction-completion total. Production and preservation are included. Unit sums may mix project statuses.')
        if g['rows']:
            show=[{'Project':row.get('PROJECT_NAME'),'Status':row.get('STATUS_PUBLIC'),'Units reported':row.get('TOTAL_AFFORDABLE_UNITS')} for row in g['rows']]
            st.dataframe(pd.DataFrame(show),hide_index=True,use_container_width=True)
            st.download_button('Download DC GIS records (CSV)',pd.DataFrame(g['rows']).to_csv(index=False).encode('utf-8'),file_name='DC_GIS_Planning_Area_Projects.csv',mime='text/csv')
        st.markdown(f'[Official DC GIS layer and methodology]({GIS_LAYER})')
    except (DataUnavailable,ValueError) as exc:
        st.warning(f'DC GIS unavailable or unverified: {exc}. Historical evidence above remains available; no live count is shown.')
    key=census_key()
    try:
        # Optionally also configure CENSUS_API_KEY in Streamlit secrets.
        if not key:
            try:key=str(st.secrets.get('CENSUS_API_KEY','')).strip()
            except Exception:key=''
        if not key:
            st.info('Optional ACS Census-tract income data are disabled because a Census API key has not been configured in Streamlit secrets. No key is needed for the rest of DC Housing Lab.')
        else:
            a=cached_acs(place,key)
            st.markdown(f"**2024 ACS 5-year Census tract:** {a['geography']} | retrieved {a['retrieved_at']} UTC")
            if a['median_household_income'] is None:
                st.warning('Census median household income unavailable for this tract.')
            else:
                st.metric('Census-tract median household income',f"${a['median_household_income']:,}")
                if a['median_household_income_moe'] is not None:st.caption(f"ACS margin of error: ±${a['median_household_income_moe']:,}")
            st.caption(a['note']+' Estimates are in 2024 inflation-adjusted dollars.')
            st.markdown(f"[Census ACS 2024 5-year source]({ACS_BASE})")
    except (DataUnavailable,ValueError) as exc:
        st.warning(f'ACS unavailable or unverified: {exc}. No tract value is shown.')
    st.divider()
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
    st.caption('Loan proceeds reduce the capital funding gap. The economic margin gap uses unlevered property value and is unchanged by a repayable loan. Annual public and private loan payments are included in the total DSCR shown in Build a project.')
    st.markdown('#### Compare neighborhood baselines (illustrative)')
    rows=[]
    for name in NEIGHBORHOODS:
        x=analyze(neighborhood_inputs(name,scenario))
        rows.append({'Neighborhood':name,'Homes':x['units'],'Restricted':x['restricted_units'],'Market rent ($/mo)':x['market_rent'],'Cost per home ($)':x['cost_per_unit'],'Economic margin gap ($M)':round(x['margin_gap']/1e6,1)})
    st.dataframe(pd.DataFrame(rows).style.format({'Homes':'{:,.0f}','Restricted':'{:,.0f}','Market rent ($/mo)':lambda x:money(x),'Cost per home ($)':lambda x:money(x),'Economic margin gap ($M)':lambda x: money(x*1e6,compact=True)}),hide_index=True,use_container_width=True)

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
    st.download_button('Download one-page project summary (PDF)',
        data=create_student_pdf(team.strip()[:40] or 'Unassigned',place,priority,p,r),
        file_name='dc_housing_lab_student_proposal.pdf',mime='application/pdf',
        use_container_width=True)
    if st.button('Save proposal',type='primary'):
        if not team.strip():st.error('Enter your team name first.')
        else:
            st.session_state.saved.append({'Team':team.strip()[:40],'Neighborhood':place,'Priority':priority,'Homes':p.units,'Restricted homes':r['restricted_units'],'Restricted rent ($)':p.affordable_rent,'Grant ($M)':p.grant_m,'Land credit ($M)':p.land_credit_m,'Loan ($M)':p.loan_m,'Economic margin gap ($M)':round(r['margin_gap']/1e6,2),'Private debt used ($M)':round(r['funded_private_debt']/1e6,2),'Required equity ($M)':round(r['equity_required']/1e6,2),'Total DSCR (x)':round(r['total_dscr'],2) if r['total_dscr'] is not None else None,'Goals met':sum(goals)})
            st.success('Saved to this browser session. Download a CSV to retain it.')
    if st.session_state.saved:
        df=pd.DataFrame(st.session_state.saved)
        st.dataframe(df.style.format({c:(lambda x:money(x*1e6,compact=True)) for c in df.columns if '($M)' in c}).format({c:lambda x: money(x) for c in df.columns if '($)' in c}).format({c:'{:,.0f}' for c in ['Homes','Restricted homes'] if c in df.columns}),hide_index=True,use_container_width=True)
        st.download_button('Download proposal(s) CSV',df.to_csv(index=False),'dc_housing_proposals_v1_5.csv','text/csv')
    files=st.file_uploader('Instructor: combine student exports here',type=['csv'],accept_multiple_files=True)
    loaded=[]
    for file in files or []:
        try:
            x=pd.read_csv(file)
            if {'Team','Homes','Restricted homes','Economic margin gap ($M)'}.issubset(x.columns):loaded.append(x)
            else:st.warning(f'{file.name}: does not match proposal format')
        except Exception as exc:st.warning(f'{file.name}: could not open ({exc})')
    if loaded:
        combined=pd.concat(([pd.DataFrame(st.session_state.saved)] if st.session_state.saved else [])+loaded,ignore_index=True)
        st.dataframe(combined.style.format({c:(lambda x:money(x*1e6,compact=True)) for c in combined.columns if '($M)' in c}).format({c:lambda x:money(x) for c in combined.columns if '($)' in c}).format({c:'{:,.0f}' for c in ['Homes','Restricted homes'] if c in combined.columns}),hide_index=True,use_container_width=True)
        st.bar_chart(combined.set_index('Team')[['Homes','Restricted homes']])
        st.download_button('Download combined class results',combined.to_csv(index=False),'class_results.csv','text/csv')
    st.caption('No live multi-user synchronization or database. Student files must be shared with the instructor for aggregation.')

with tabs[5]:
    st.subheader('Stress test a development')
    st.write('Change all-in development cost and cap rates to see how the funding requirement changes.')
    st.caption('Each table cell is the unlevered economic gap to the illustrative margin; it does not depend on public loan principal. A positive number is a deficit; a negative number is a surplus. Current subsidy and loan assumptions remain fixed.')
    sensitivity_df=pd.DataFrame(sensitivity(p))
    st.dataframe(sensitivity_df.style.format({c:lambda v:money(v,compact=True) for c in sensitivity_df.columns if c!='Cost change'}),hide_index=True,use_container_width=True)
    minimum=minimum_grant_to_margin(p)
    st.metric('Minimum total grant to satisfy economic margin',fm(minimum))
    st.caption(f'Existing grant: {fm(r["grant"])}. Additional grant necessary: {fm(max(0,minimum-r["grant"]))}. This is a screening calculation, not a determination of subsidy eligibility.')
    st.divider()
    st.subheader('Compare two development strategies')
    left,right=st.columns(2)
    with left:
        if st.button('Save current design as A',use_container_width=True):
            st.session_state.comparison['A']=snapshot(p,'Scenario A')
            st.success('Saved A in this browser session.')
    with right:
        if st.button('Save current design as B',use_container_width=True):
            st.session_state.comparison['B']=snapshot(p,'Scenario B')
            st.success('Saved B in this browser session.')
    if st.session_state.comparison:
        comparison_df=pd.DataFrame([{k:v for k,v in item.items() if k!='inputs'} for item in st.session_state.comparison.values()])
        fmt={c:(lambda v:money(v,compact=True) if pd.notna(v) else 'N/A') for c in comparison_df.columns if '($)' in c}
        fmt.update({'Affordable share (%)':lambda v:percentage(v,1),'Affordable homes':'{:,.0f}','Homes':'{:,.0f}'})
        st.dataframe(comparison_df.style.format(fmt),hide_index=True,use_container_width=True)
        st.download_button('Download comparison CSV',comparison_df.to_csv(index=False),'dc_housing_lab_comparison.csv','text/csv')
    st.caption('Saved scenarios are local to this browser session; no shared student database is used.')
    with st.expander('Explain the economics',expanded=True):
        st.markdown("""**NOI:** Rent less vacancy and operating expenses, before debt and income taxes.

**Cap rate:** NOI divided by property value; a higher rate reduces implied value at equal NOI.

**AMI:** Area median income; actual income limits and allowable rents vary by program, fiscal year, and household size.

**Economic margin gap:** Development cost × (1 + margin) minus cash grant minus unlevered asset value. It is not a capital stack shortfall or an investor IRR.

**Capital funding gap:** Net development cost minus grants, public loan proceeds, illustrative private debt and committed equity. This is a sources-and-uses check, not evidence that capital is actually available.

**Total DSCR:** NOI ÷ (annual public debt service + annual private debt service). Public-only DSCR is shown separately and must not be mistaken for total coverage.

**Debt capacity:** The minimum of DSCR-based, LTV-based and LTC-based limits. Private loan used cannot exceed the entered requested commitment.

**Equity requirement:** Net development cost less grants, public loan proceeds and supportable private debt, floored at zero; compare to entered committed equity. This is a static sources-and-uses approximation, not a project IRR.

**Grant vs. loan:** Grants are permanent public support; loans require repayment. A land discount carries an opportunity cost.

**Sensitivity:** Each cell recalculates the same model with independent cap-rate and cost changes.""")

with tabs[6]:
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
- A repayable public loan supplies capital and requires annual payments. Its payments do not reduce NOI or capitalized unlevered property value. The app reports both public-only and total DSCR.
- Required economic margin compares unlevered stabilized value plus grants against land-adjusted development cost plus a classroom return buffer. It is **not an investor IRR, developer fee, financing commitment, tax-credit model, or debt-sizing exercise**.
- Increasing units assumes scalable costs; real zoning, parcels, land value, site constraints, infrastructure and entitlement approvals can prevent that outcome.
- Actual restricted rents depend on the program, AMI vintage, household/unit sizing, and allowances. The illustration cannot establish legal eligibility.
- A project can satisfy this simplified mathematical test while still being impossible to finance; likewise a project that fails it may be possible with other sources of capital.''')
    st.markdown('Relevant official resources: [DC Office of Planning](https://planning.dc.gov/) · [DC DHCD](https://dhcd.dc.gov/) · [HUD income limits](https://www.huduser.gov/portal/datasets/il.html).')
st.divider();st.caption('DC Housing Lab v1.9 • October 2026 • Illustrative classroom tool; not investment, legal or eligibility advice.')

with tabs[7]:
    st.subheader('Ten-year operating and affordability preservation outlook')
    st.caption('Starts with the stabilized operating assumptions. Market and restricted rents grow separately; operating expenses, replacement reserves and debt repayment are forecast annually. Illustrative analysis, not a regulated rent schedule or investment offering.')
    f1,f2,f3=st.columns(3)
    with f1:
        mg=st.slider('Market rent growth (% / year)',-3.0,8.0,3.0,0.5,key='f_market')
        ag=st.slider('Restricted rent growth (% / year)',-3.0,8.0,1.5,0.5,key='f_restricted')
        exp=st.slider('Operating expense inflation (% / year)',0.0,10.0,3.5,0.5,key='f_expense')
    with f2:
        vac=st.slider('Projected vacancy / bad debt (%)',0.0,20.0,float(p.vacancy_pct),0.5,key='f_vacancy')
        reserve=st.slider('Year 1 replacement reserve ($ / home / year)',0,2000,400,50,key='f_reserve')
    with f3:
        exit_cap=st.slider('Exit capitalization rate (%)',3.0,10.0,6.0,0.25,key='f_exit_cap')
        exit_cost=st.slider('Disposition costs (% of sale price)',0.0,8.0,2.0,0.5,key='f_sale_cost')
    a=ForecastAssumptions(mg,ag,exp,vac,reserve,exit_cap,exit_cost)
    forecast=project(p,r,a)
    x1,x2,x3,x4=st.columns(4)
    x1.metric('Year 10 NOI',fm(forecast['rows'][-1]['noi']))
    x2.metric('Net sale to equity',fm(forecast['net_sale_to_equity']))
    x3.metric('Equity multiple',f"{forecast['equity_multiple']:.2f}×" if forecast['equity_multiple'] is not None else 'N/A')
    x4.metric('10-year equity IRR',f"{forecast['equity_irr']*100:.1f}%" if forecast['equity_irr'] is not None else 'N/A')
    if forecast['expense_growth_exceeds_restricted_growth']:
        st.warning('Expense inflation exceeds restricted rent growth. This can compress operating margins, especially as the affordable housing share increases.')
    if forecast['minimum_cash_flow']<0:
        st.error('At least one forecast year has negative operating cash flow after reserves and modeled debt service.')
    if r['additional_equity_needed']>0:
        st.warning('Capital stack still has an unfunded equity requirement. Return metrics assume the full required equity is contributed at inception.')
    df_f=pd.DataFrame(forecast['rows'])
    st.line_chart(df_f.set_index('year')[['noi','cash_flow_to_equity']],x_label='Operating year',y_label='Annual dollars ($)')
    st.markdown('#### Annual projected operations and debt amortization')
    annual_cols=['year','scheduled_rent','effective_income','operating_expenses','noi','replacement_reserve','total_debt_service','cash_flow_to_equity','public_balance','private_balance']
    labels={'year':'Year','scheduled_rent':'Scheduled rent ($)','effective_income':'Effective income ($)','operating_expenses':'Operating expenses ($)','noi':'NOI ($)','replacement_reserve':'Reserves ($)','total_debt_service':'Debt service ($)','cash_flow_to_equity':'Cash flow to equity ($)','public_balance':'Public loan balance ($)','private_balance':'Private loan balance ($)'}
    output=df_f[annual_cols].rename(columns=labels)
    st.dataframe(output.style.format({c:money for c in output.columns if c.endswith('($)')}),use_container_width=True,hide_index=True)
    st.download_button('Download ten-year forecast (CSV)',output.to_csv(index=False).encode('utf-8'),file_name='dc_housing_lab_10_year_forecast.csv',mime='text/csv')
    with st.expander('Disposition method, investor returns and model limitations'):
        st.write(f"Year 11 projected NOI: {money(forecast['year_11_noi'])}; gross exit value: {money(forecast['sale_price'])}; selling costs: {money(forecast['selling_cost'])}; loan balances repaid at sale: {money(forecast['ending_debt'])}.")
        st.write('Value = Year 11 NOI / exit cap rate. Net sale = gross sale price minus selling costs and outstanding public and private loan balances. IRR uses initial total required equity, ten annual operating cash flows, and net sale proceeds in Year 10. A negative net sale represents a residual obligation rather than a guaranteed equity distribution.')
        st.write('Loan amortization uses original balances and terms; maturity refinancing, balloon provisions, capital improvements beyond modeled reserves, income taxes, reinvestment, income-limit updates, tax credit compliance, and public-loan cash sweeps are not modeled. Restricted rent growth is a hypothetical assumption, not a statement of legally permitted increases. Multiple IRRs or nonconventional cash flows may require more detailed analysis.')


with tabs[8]:
    st.subheader('Public subsidy efficiency | Policy-maker perspective')
    st.caption('Compare upfront public outlays with the estimated present value of support. This is not a full governmental fiscal impact or cost-benefit analysis.')
    pa,pb=st.columns(2)
    with pa:
        term=st.slider('Affordability restriction period (years)',10,60,30,5,key='pe_restriction_years')
    with pb:
        public_discount=st.slider('Public discount rate (%)',0.0,12.0,5.0,0.5,key='pe_discount_rate')
    policy=evaluate(p,r,PublicPolicyAssumptions(term,public_discount))
    one,two,three,four=st.columns(4)
    one.metric('Restricted homes',integer(policy['restricted_homes']))
    two.metric('Restricted home-years',integer(policy['restricted_unit_years']))
    three.metric('Estimated public support (PV)',fm(policy['net_public_support_pv']))
    four.metric('Support (PV) per restricted home-year',money(policy['support_pv_per_restricted_unit_year']) if policy['support_pv_per_restricted_unit_year'] is not None else 'N/A')
    st.markdown('#### Public resource accounting')
    ptable=pd.DataFrame([
        {'Item':'Nonrepayable cash grant','Amount ($)':policy['grant'],'Method':'Full face amount'},
        {'Item':'Public land value contributed','Amount ($)':policy['land_contribution_value'],'Method':'Assumed land cost discount; public opportunity cost'},
        {'Item':'Repayable loan amount (gross funding)','Amount ($)':policy['loan_face'],'Method':'Gross cash advanced; not equivalent to a grant'},
        {'Item':'Estimated concessional loan benefit (PV)','Amount ($)':policy['loan_pv_concession'],'Method':'Loan face less PV of amortizing repayments'},
        {'Item':'Combined estimated public support (PV)','Amount ($)':policy['net_public_support_pv'],'Method':'Grant + land contribution + loan concession'}])
    st.dataframe(ptable.style.format({'Amount ($)':money}),hide_index=True,use_container_width=True)
    st.download_button('Download public subsidy efficiency (CSV)',ptable.to_csv(index=False).encode('utf-8'),file_name='dc_housing_lab_public_efficiency.csv',mime='text/csv',key='download_public_efficiency')
    st.markdown('#### Grant versus loan — equal face amount')
    face=st.slider('Compare additional public commitment ($M)',0,30,10,1,key='pe_equal_face')*1e6
    discount_loan=evaluate(p,analyze(replace(p,loan_m=face/1e6,grant_m=0,land_credit_m=0)),PublicPolicyAssumptions(term,public_discount))
    table=pd.DataFrame([
      {'Instrument':'Nonrepayable grant','Public capital advanced ($)':face,'Net public support PV ($)':face},
      {'Instrument':'Repayable amortizing loan','Public capital advanced ($)':face,'Net public support PV ($)':discount_loan['loan_pv_concession']}])
    st.dataframe(table.style.format({'Public capital advanced ($)':money,'Net public support PV ($)':money}),hide_index=True,use_container_width=True)
    st.caption('Loan illustration uses the current public loan rate and amortization. The public discount rate is a chosen classroom assumption, not an official DC borrowing rate. Negative loan concession values are possible when the loan yield exceeds the assumed discount rate.')
    if not policy['restricted_homes']:
        st.warning('No restricted homes: per-restricted-home metrics are N/A, not zero.')
    if policy['restricted_homes'] and p.affordable_rent>p.market_rent:
        st.warning('Restricted rent exceeds market rent in this scenario; the affordability designation is not proof of economic affordability.')
    with st.expander('Interpretation, limitations and recommended classroom questions'):
        for caution in policy['cautions']:st.write('• '+caution)
        st.write('How should the District evaluate fewer deeply affordable units against more moderately restricted units? How should the public value of contributed land be counted? What if the borrower cannot repay the loan?')
        st.write('A 30-year restriction is assumed if selected; the application does not verify a legally binding agreement. Comparing programs also requires incomes served, persistence, displacement avoided, location, and quality—not just cost per unit.')

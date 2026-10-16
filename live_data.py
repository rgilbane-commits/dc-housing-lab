"""Optional live public observations; strictly separate from the housing feasibility model.

Geography: DC GIS projects filtered by exact planning-area name; ACS is the
single Census tract containing an illustrative neighborhood center, NOT the
whole neighborhood. All network calls have timeouts and explicit failures.
"""
from datetime import datetime, timezone
import os
import requests

GIS_LAYER='https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/FeatureServer/62'
ACS_BASE='https://api.census.gov/data/2024/acs/acs5'
GEOCODER='https://geocoding.geo.census.gov/geocoder/geographies/coordinates'
GIS_FIELDS=('OBJECTID','PROJECT_NAME','PLANNING_AREA','STATUS_PUBLIC','TOTAL_AFFORDABLE_UNITS',
            'AFFORDABLE_UNITS_PRODUCTION','AFFORDABLE_UNITS_PRESERVED','GIS_LAST_MOD_DTTM')
CENTERS={
 'Friendship Heights / Ward 3':(38.9593,-77.0847,'Rock Creek West'),
 'Columbia Heights / Ward 1':(38.9289,-77.0327,'Mid-City'),
 'Congress Heights / Ward 8':(38.8437,-76.9889,'Far Southeast and Southwest')}

class DataUnavailable(RuntimeError):
    pass

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def get_json(url, params, session=None, timeout=9):
    try:
        response=(session or requests).get(url,params=params,timeout=timeout)
        response.raise_for_status()
        payload=response.json()
    except (requests.RequestException,ValueError) as exc:
        raise DataUnavailable(f'Public source unavailable: {type(exc).__name__}') from exc
    if isinstance(payload,dict) and ('error' in payload or 'errors' in payload):
        raise DataUnavailable('Source returned an API error; see provider documentation or verify credentials.')
    return payload

def clean_count(value):
    if value is None or value == '':return None
    try:
        x=float(value)
        return x if x>=0 and x==x else None
    except (TypeError,ValueError): return None

def summarize_projects(records):
    """Does NOT equate projects started/completed since 2015 with current stock."""
    records=list(records)
    ids=[r.get('OBJECTID') for r in records]
    if any(i is None for i in ids) or len(ids)!=len(set(ids)):
        raise DataUnavailable('Unreliable GIS project identifiers; refusing a potentially duplicated count.')
    totals=[clean_count(r.get('TOTAL_AFFORDABLE_UNITS')) for r in records]
    valid=[v for v in totals if v is not None]
    return {'project_count':len(records),'reported_unit_sum':int(round(sum(valid))),
            'reported_units_rows':len(valid),'missing_units_rows':len(records)-len(valid)}

def fetch_gis(neighborhood, session=None, page_size=500, max_pages=20):
    if neighborhood not in CENTERS:raise ValueError('Unknown neighborhood')
    area=CENTERS[neighborhood][2]
    where="PLANNING_AREA = '"+area.upper().replace("'","''")+"'"
    records=[]; asof=utc_now()
    for page in range(max_pages):
        data=get_json(GIS_LAYER+'/query',{'where':where,'outFields':','.join(GIS_FIELDS),
             'returnGeometry':'false','orderByFields':'OBJECTID ASC','resultOffset':page*page_size,
             'resultRecordCount':page_size,'f':'json'},session=session)
        if not isinstance(data,dict) or not isinstance(data.get('features'),list):
            raise DataUnavailable('GIS response missing expected features array.')
        batch=[f.get('attributes',{}) for f in data['features']]
        if not all(isinstance(r,dict) for r in batch):
            raise DataUnavailable('Unexpected GIS response fields.')
        records.extend(batch)
        if len(batch)<page_size and not data.get('exceededTransferLimit'):break
    else:
        raise DataUnavailable('GIS pagination cap reached; incomplete data were not reported.')
    if not records:
        # A zero-row attribute filter is not evidence that the planning area has
        # zero projects. Query the service independently and inspect its values.
        # This prevents a schema/value mismatch from being published as a fact.
        observed=set()
        for fallback_page in range(max_pages):
            sample=get_json(GIS_LAYER+'/query',{'where':'1=1',
                 'outFields':'OBJECTID,PLANNING_AREA', 'returnGeometry':'false',
                 'orderByFields':'OBJECTID ASC', 'resultOffset':fallback_page*page_size,
                 'resultRecordCount':page_size,'f':'json'},session=session)
            if not isinstance(sample,dict) or not isinstance(sample.get('features'),list):
                raise DataUnavailable('Unable to validate zero result: GIS fallback query failed.')
            batch=sample['features']
            observed.update(str(f.get('attributes',{}).get('PLANNING_AREA') or '').strip()
                            for f in batch if isinstance(f.get('attributes'),dict))
            if len(batch)<page_size and not sample.get('exceededTransferLimit'):
                break
        else:
            raise DataUnavailable('Unable to verify empty planning-area result: GIS fallback pagination incomplete.')
        if not observed or observed == {''}:
            raise DataUnavailable('GIS returned no usable planning-area values; zero project count cannot be verified.')
        examples=', '.join(sorted(v for v in observed if v)[:5])
        raise DataUnavailable('No GIS records matched '+repr(area)+
            '. This may be a planning-area naming mismatch or a true zero; '
            'zero is NOT verified. Source values include: '+examples)
    if any(str(r.get('PLANNING_AREA') or '').strip().casefold() != area.casefold() for r in records):
        raise DataUnavailable('GIS planning-area mismatch; results rejected.')
    return {'status':'live','area':area,'retrieved_at':asof,'rows':records,'metrics':summarize_projects(records)}

def parse_census_value(value):
    try:
        n=int(value)
        return n if n>=0 else None
    except (TypeError,ValueError):return None

def fetch_acs(neighborhood,api_key,session=None):
    if neighborhood not in CENTERS:raise ValueError('Unknown neighborhood')
    if not api_key:raise DataUnavailable('Census API key not configured; ACS live data disabled.')
    lat,lon,_=CENTERS[neighborhood]
    geocode=get_json(GEOCODER,{'x':lon,'y':lat,'benchmark':'Public_AR_Current',
                  'vintage':'Current_Current','format':'json'},session=session)
    tracts=geocode.get('result',{}).get('geographies',{}).get('Census Tracts',[])
    if len(tracts)!=1:raise DataUnavailable('Could not uniquely identify a Census tract at neighborhood marker.')
    tract=str(tracts[0].get('TRACT',''))
    if len(tract)!=6 or not tract.isdigit():raise DataUnavailable('Census tract identifier invalid.')
    data=get_json(ACS_BASE,{'get':'NAME,B19013_001E,B19013_001M',
                'for':'tract:'+tract,'in':'state:11 county:001','key':api_key},session=session)
    # B25064 is not universally available on modern ACS; handle unavailable below
    if not isinstance(data,list) or len(data)!=2 or len(data[0])!=len(data[1]):
        raise DataUnavailable('Unexpected Census ACS response shape.')
    row=dict(zip(data[0],data[1]))
    return {'status':'live','retrieved_at':utc_now(),'tract':tract,'geography':row.get('NAME'),
            'median_household_income':parse_census_value(row.get('B19013_001E')),
            'median_household_income_moe':parse_census_value(row.get('B19013_001M')),
            'source_year':2024,'source_url':ACS_BASE,'note':'Single Census tract containing neighborhood center; not a neighborhood-wide estimate.'}

def census_key():
    return os.getenv('CENSUS_API_KEY','').strip()

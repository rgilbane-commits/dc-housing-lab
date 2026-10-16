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
            'AFFORDABLE_UNITS_PRODUCTION','AFFORDABLE_UNITS_PRESERVED','GIS_LAST_MOD_DTTM','LATITUDE','LONGITUDE')
CENTERS={
 'Friendship Heights / Ward 3':(38.9593,-77.0847,'Rock Creek West'),
 'Columbia Heights / Ward 1':(38.9289,-77.0327,'Mid-City'),
 'Congress Heights / Ward 8':(38.8437,-76.9889,'Far Southeast and Southwest'), 'Downtown / Ward 2':(38.8987,-77.028,'Central Washington'),
 'Takoma / Ward 4':(38.9734,-77.0171,'Rock Creek East'),
 'Brookland / Ward 5':(38.9323,-76.995,'Upper Northeast'),
 'Capitol Hill / Ward 6':(38.8864,-76.9958,'Capitol Hill'),
 'Deanwood / Ward 7':(38.8995,-76.9277,'Far Northeast and Southeast'),
 'Dupont Circle / Ward 2':(38.9096,-77.0434,'Near Northwest'),
 'Navy Yard / Ward 6':(38.874,-77.001,'Lower Anacostia Waterfront and Near Southwest')}

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
        return int(x) if x>=0 and x==x and x.is_integer() else None
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

def normalize_area(value):
    """Normalize typography only; never guess unrelated geographic names."""
    import re
    name = str(value or '').strip().upper().replace('&', ' AND ')
    return ' '.join(re.sub(r'[^A-Z0-9]+', ' ', name).split())


def discover_gis_areas(session=None):
    """Read source literals rather than relying on application-supplied spelling."""
    data = get_json(GIS_LAYER+'/query', {
        'where':'1=1', 'outFields':'PLANNING_AREA', 'returnGeometry':'false',
        'returnDistinctValues':'true', 'orderByFields':'PLANNING_AREA ASC',
        'f':'json'}, session=session)
    if not isinstance(data,dict) or not isinstance(data.get('features'),list):
        raise DataUnavailable('Planning-area discovery response is invalid.')
    if data.get('exceededTransferLimit'):
        raise DataUnavailable('Planning-area discovery is incomplete (service transfer limit).')
    values=sorted({str(item.get('attributes',{}).get('PLANNING_AREA') or '').strip()
                   for item in data['features'] if isinstance(item,dict) and
                   isinstance(item.get('attributes'),dict)})
    values=[v for v in values if v]
    if not values:raise DataUnavailable('No valid planning-area names discovered.')
    return values


def match_gis_area(target, source_values):
    normalized=normalize_area(target)
    matches=[v for v in source_values if normalize_area(v)==normalized]
    if len(matches)!=1:
        examples=', '.join(source_values[:8])
        raise DataUnavailable(f'Cannot uniquely match planning area {target!r}; '
                              f'matches={len(matches)}. Available source values: {examples}')
    return matches[0]


def fetch_gis(neighborhood, session=None, page_size=500, max_pages=20):
    if neighborhood not in CENTERS:raise ValueError('Unknown neighborhood')
    if page_size<1 or max_pages<1:raise ValueError('Invalid pagination limits')
    requested_area=CENTERS[neighborhood][2]
    source_values=discover_gis_areas(session=session)
    area=match_gis_area(requested_area,source_values)
    where="PLANNING_AREA = '"+area.replace("'","''")+"'"
    count=get_json(GIS_LAYER+'/query',{'where':where,'returnCountOnly':'true','f':'json'},session=session)
    if not isinstance(count,dict) or type(count.get('count')) is not int or count['count']<0:
        raise DataUnavailable('GIS count response missing or invalid; refusing incomplete totals.')
    expected=count['count'];records=[];asof=utc_now()
    if expected>page_size*max_pages:
        raise DataUnavailable('Project count exceeds pagination safety limit.')
    for page in range(max_pages):
        if len(records)>=expected:break
        data=get_json(GIS_LAYER+'/query',{'where':where,'outFields':','.join(GIS_FIELDS),
            'returnGeometry':'false','orderByFields':'OBJECTID ASC','resultOffset':page*page_size,
            'resultRecordCount':min(page_size,expected-len(records)),'f':'json'},session=session)
        if not isinstance(data,dict) or not isinstance(data.get('features'),list):
            raise DataUnavailable('GIS page has no valid features array.')
        batch=[f.get('attributes') if isinstance(f,dict) else None for f in data['features']]
        if not all(isinstance(r,dict) for r in batch):
            raise DataUnavailable('GIS page contains invalid attributes.')
        if not batch:raise DataUnavailable('GIS pagination terminated before expected project count.')
        records.extend(batch)
    final_count=get_json(GIS_LAYER+'/query',{'where':where,'returnCountOnly':'true','f':'json'},session=session)
    if not isinstance(final_count,dict) or final_count.get('count')!=expected:
        raise DataUnavailable('GIS count changed during pagination; refusing inconsistent snapshot.')
    if len(records)!=expected:
        raise DataUnavailable(f'GIS incomplete: expected {expected} projects, received {len(records)}.')
    if any(normalize_area(r.get('PLANNING_AREA'))!=normalize_area(area) for r in records):
        raise DataUnavailable('GIS planning-area mismatch; results rejected.')
    metrics=summarize_projects(records)
    return {'status':'live_verified' if expected else 'verified_zero', 'area':area,
            'requested_area':requested_area,'retrieved_at':asof,'rows':records,
            'metrics':metrics,'expected_count':expected,
            'source_area_values':source_values,
            'data_quality':('partial_units' if metrics['missing_units_rows'] else 'complete_units')}

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

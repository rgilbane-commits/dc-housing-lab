"""2024 ACS 5-year tract-to-planning-area approximate normalization.

Never treat area-weighted allocations as exact population tabulations. Fail closed.
"""
import io
import math
import zipfile
import requests
import shapefile
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer

ACS_URL = "https://api.census.gov/data/2024/acs/acs5"
TRACT_ZIP = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_11_tract_500k.zip"
SOURCE_YEAR = "2024 ACS 5-year"
# 2024 ACS geographic estimates use 2020-based census tract boundaries.
MIN_COVERAGE = 0.995
MAX_ZIP_BYTES = 15_000_000

class DenominatorUnavailable(Exception):
    pass

def parse_acs(payload):
    if not isinstance(payload,list) or not payload or not isinstance(payload[0],list):
        raise DenominatorUnavailable('ACS response is not a table')
    fields=payload[0]
    required=['B11001_001E','B25001_001E','state','county','tract']
    moes_available=all(f in fields for f in ('B11001_001M','B25001_001M'))
    if not all(f in fields for f in required):raise DenominatorUnavailable('Missing required ACS columns')
    data={}
    for values in payload[1:]:
        if not isinstance(values,list) or len(values)!=len(fields):raise DenominatorUnavailable('Malformed ACS row')
        r=dict(zip(fields,values))
        geoid=''.join(r.get(k,'') for k in ('state','county','tract'))
        if len(geoid)!=11 or not geoid.isdigit() or not geoid.startswith('11') or geoid in data:
            raise DenominatorUnavailable('Invalid/duplicate tract GEOID')
        try:
            hh=int(r['B11001_001E']); housing=int(r['B25001_001E'])
        except (ValueError,TypeError):raise DenominatorUnavailable('Invalid ACS estimate')
        if hh<0 or housing<0 or hh>housing:raise DenominatorUnavailable('Invalid household/housing count')
        if moes_available:
            try:
                hh_moe=int(r['B11001_001M']); hu_moe=int(r['B25001_001M'])
            except (ValueError,TypeError):raise DenominatorUnavailable('Invalid ACS margin of error')
            if hh_moe<0 or hu_moe<0:raise DenominatorUnavailable('Negative ACS margin of error')
            data[geoid]=(hh,housing,hh_moe,hu_moe)
        else:
            data[geoid]=(hh,housing)
    if not data:raise DenominatorUnavailable('Empty ACS response')
    return data

def load_tract_shapes(blob):
    if not isinstance(blob,bytes) or len(blob)>MAX_ZIP_BYTES:raise DenominatorUnavailable('Census boundary archive missing/too large')
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names=z.namelist()
            if any('/' in n or '..' in n for n in names):raise DenominatorUnavailable('Unsafe archive path')
            shp=next(n for n in names if n.lower().endswith('.shp'))
            stem=shp[:-4]
            shx=z.read(stem+'.shx'); dbf=z.read(stem+'.dbf')
            reader=shapefile.Reader(shp=io.BytesIO(z.read(shp)),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf))
            keys=[f[0] for f in reader.fields[1:]]
            if 'GEOID' not in keys:raise DenominatorUnavailable('Tract GEOID field missing')
            result={}
            for sr in reader.iterShapeRecords():
                record=dict(zip(keys,list(sr.record))); geoid=str(record['GEOID'])
                g=shape(sr.shape.__geo_interface__)
                if geoid in result or len(geoid)!=11 or not g.is_valid or g.is_empty:
                    raise DenominatorUnavailable('Invalid/duplicate tract geometry')
                result[geoid]=g
    except (OSError,ValueError,KeyError,StopIteration,zipfile.BadZipFile,shapefile.ShapefileException) as exc:
        raise DenominatorUnavailable('Census boundary archive invalid') from exc
    if not result:raise DenominatorUnavailable('No Census tract geometries')
    return result

def aggregate(boundary,tracts,acs,coverage_required=MIN_COVERAGE):
    """Area-weighted estimates in EPSG:5070; not population-weighted interpolation."""
    projector=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True).transform
    polygon=transform(projector,shape(boundary['geojson']))
    if not polygon.is_valid or polygon.is_empty or polygon.area<=0:raise DenominatorUnavailable('Invalid planning-area boundary')
    covered=0.; hh=0.; homes=0.; count=0; missing=[]
    hh_moe_sq=0.; housing_moe_sq=0.; moe_available=all(len(row)>=4 for row in acs.values())
    overlaps=[]
    for geoid,geom in tracts.items():
        g=transform(projector,geom)
        if not g.intersects(polygon):continue
        intersection=g.intersection(polygon).area
        if intersection<=0:continue
        if geoid not in acs:missing.append(geoid);continue
        fraction=min(1.,intersection/g.area)
        covered+=intersection;count+=1
        overlaps.append(g.intersection(polygon))
        hh+=acs[geoid][0]*fraction;homes+=acs[geoid][1]*fraction
        if moe_available:
            hh_moe_sq+=(acs[geoid][2]*fraction)**2
            housing_moe_sq+=(acs[geoid][3]*fraction)**2
    # The area sum must not exceed the official polygon's area: duplicate or overlapping
    # Census tracts otherwise make a falsely complete denominator.
    if covered>polygon.area*(1+1e-6):
        raise DenominatorUnavailable('Overlapping tract geometry: summed coverage exceeds planning area')
    coverage=min(1.,covered/polygon.area)
    if missing or coverage<coverage_required or not count:
        raise DenominatorUnavailable(f'Coverage incomplete: {coverage:.1%}; missing ACS tracts: {len(missing)}')
    if hh<=0 or homes<=0:raise DenominatorUnavailable('Nonpositive geographic denominator')
    return {'households_est':hh,'housing_units_est':homes,
            'households_moe_90_proxy':math.sqrt(hh_moe_sq) if moe_available else None,
            'housing_units_moe_90_proxy':math.sqrt(housing_moe_sq) if moe_available else None,
            'moe_method':'RSS of area-weighted tract-level ACS MOEs; ignores interpolation/geographic covariance; NOT a validated planning-area confidence interval','coverage':coverage,'tracts_intersected':count,
            'method':'2024 ACS tract estimates area-weighted to DC planning polygon (EPSG:5070)',
            'year':SOURCE_YEAR,'source':ACS_URL,'boundary_source':TRACT_ZIP,
            'note':'Uniform-within-tract assumption. Area-weighted MOEs are heuristic only; unknown interpolation error can dominate. Not an official Census planning-area estimate.'}

def retrieve(census_key,boundary,session=None):
    if not census_key:raise DenominatorUnavailable('Configure CENSUS_API_KEY in Streamlit secrets')
    s=session or requests
    try:
        r=s.get(ACS_URL,params={'get':'NAME,B11001_001E,B25001_001E,B11001_001M,B25001_001M','for':'tract:*','in':'state:11','key':census_key},timeout=25)
        r.raise_for_status(); acs=parse_acs(r.json())
        r=s.get(TRACT_ZIP,timeout=25);r.raise_for_status()
        if len(r.content)>MAX_ZIP_BYTES:raise DenominatorUnavailable('Tract boundary response too large')
        tracts=load_tract_shapes(r.content)
        return aggregate(boundary,tracts,acs)
    except (requests.RequestException,ValueError) as exc:raise DenominatorUnavailable(f'Upstream Census retrieval failed: {type(exc).__name__}') from exc

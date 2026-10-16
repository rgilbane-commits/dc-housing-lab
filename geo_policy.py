"""Fail-closed, topology-aware DC planning-area geography (ArcGIS rings / WGS84)."""
import math
from shapely.geometry import Polygon, Point, mapping, shape
from shapely.ops import unary_union
from shapely.validation import explain_validity
from live_data import get_json, DataUnavailable, normalize_area, CENTERS, utc_now
PLANNING_LAYER = 'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Planning_Landuse_and_Zoning_WebMercator/MapServer/2'
AREA_NAMES = {'Friendship Heights / Ward 3':'Rock Creek West', 'Columbia Heights / Ward 1':'Mid-City', 'Congress Heights / Ward 8':'Far Southeast and Southwest'}

def _signed_area(ring):
    return sum((a[0]*b[1]-b[0]*a[1]) for a,b in zip(ring,ring[1:]))/2

def _geometry(rings):
    """ArcGIS standard: clockwise shells and counterclockwise holes in lon/lat."""
    shells=[]; holes=[]
    if not isinstance(rings,list) or not rings: raise DataUnavailable('No GIS polygon rings.')
    for ring in rings:
        try:
            xy=[(float(p[0]),float(p[1])) for p in ring]
        except (TypeError,ValueError,IndexError) as exc:raise DataUnavailable('Malformed polygon coordinates.') from exc
        if len(xy)<4 or xy[0]!=xy[-1] or len(set(xy[:-1]))<3 or any(not(math.isfinite(x) and math.isfinite(y) and -77.3<x<-76.7 and 38.7<y<39.1) for x,y in xy):
            raise DataUnavailable('Invalid or unclosed boundary geometry.')
        ring_polygon=Polygon(xy)
        if not ring_polygon.is_valid or ring_polygon.area<=0:raise DataUnavailable('Invalid ring topology.')
        if _signed_area(xy)<0:shells.append(ring_polygon)
        else:holes.append(ring_polygon)
    if not shells:raise DataUnavailable('No clockwise exterior ring; refusing ambiguous topology.')
    result=unary_union(shells)
    for hole in holes:
        if not result.contains(hole.representative_point()):raise DataUnavailable('Hole outside exterior boundaries.')
        result=result.difference(hole)
    if not result.is_valid or result.is_empty or result.geom_type not in ('Polygon','MultiPolygon'):
        raise DataUnavailable('Invalid planning-area polygon topology: '+explain_validity(result))
    return result

def boundary_geometry(name,session=None):
    if name not in AREA_NAMES:raise ValueError('Unsupported neighborhood')
    target=AREA_NAMES[name]
    # Discover a verified source object ID, without relying on WHERE name equality.
    payload=get_json(PLANNING_LAYER+'/query',{'where':'1=1','outFields':'OBJECTID,NAME','returnGeometry':'false','f':'json'},session=session)
    if not isinstance(payload,dict) or not isinstance(payload.get('features'),list) or payload.get('exceededTransferLimit'):
        raise DataUnavailable('Boundary identifier discovery incomplete.')
    matches=[f['attributes'] for f in payload['features'] if isinstance(f,dict) and isinstance(f.get('attributes'),dict) and normalize_area(f['attributes'].get('NAME'))==normalize_area(target)]
    if len(matches)!=1 or type(matches[0].get('OBJECTID')) is not int:raise DataUnavailable('Boundary source ID not uniquely verified.')
    oid=matches[0]['OBJECTID']
    count=get_json(PLANNING_LAYER+'/query',{'where':'OBJECTID = '+str(oid),'returnCountOnly':'true','f':'json'},session=session)
    if not isinstance(count,dict) or count.get('count')!=1:raise DataUnavailable('Boundary record count failed reconciliation.')
    result=get_json(PLANNING_LAYER+'/query',{'objectIds':str(oid),'outFields':'OBJECTID,NAME','returnGeometry':'true','outSR':4326,'f':'json'},session=session)
    if not isinstance(result,dict) or result.get('exceededTransferLimit') or len(result.get('features',[]))!=1:
        raise DataUnavailable('Boundary response incomplete or truncated.')
    feature=result['features'][0]
    if feature.get('attributes',{}).get('OBJECTID')!=oid or normalize_area(feature.get('attributes',{}).get('NAME'))!=normalize_area(target):
        raise DataUnavailable('Boundary object identifier/name changed between requests.')
    geom=_geometry((feature.get('geometry') or {}).get('rings'))
    lat,lon,_=CENTERS[name]
    if not geom.covers(Point(lon,lat)):
        raise DataUnavailable('Neighborhood reference point is outside matched boundary; reference geography unverified.')
    return {'name':feature['attributes']['NAME'],'object_id':oid,'geojson':mapping(geom),'retrieved_at':utc_now(),'source':PLANNING_LAYER}

def project_points(gis,boundary=None):
    """Exclude invalid and outside-boundary points; count each separately."""
    geom=shape(boundary['geojson']) if boundary else None
    points=[];missing=0;outside=0
    for row in gis['rows']:
        try:
            lat=float(row['LATITUDE']);lon=float(row['LONGITUDE'])
            if not(math.isfinite(lat) and math.isfinite(lon) and 38.7<lat<39.1 and -77.3<lon<-76.7):raise ValueError()
        except (ValueError,TypeError,KeyError):missing+=1;continue
        if geom is not None and not geom.covers(Point(lon,lat)):
            outside+=1;continue
        points.append({'lat':lat,'lon':lon,'name':str(row.get('PROJECT_NAME') or 'Unnamed project')[:120], 'id':row.get('OBJECTID'),'units':row.get('TOTAL_AFFORDABLE_UNITS')})
    if geom is not None and outside:
        raise DataUnavailable(f'{outside} source project coordinates fall outside their assigned planning-area polygon; map suppressed pending geographic reconciliation.')
    return points,missing

def planning_map(selected,boundary,gis):
    import folium
    from streamlit_folium import st_folium
    lat,lon,_=CENTERS[selected]
    points,missing=project_points(gis,boundary)  # Verify all markers before drawing ANY map.
    m=folium.Map(location=[lat,lon],zoom_start=12,tiles='OpenStreetMap',control_scale=True)
    folium.GeoJson(boundary['geojson'],style_function=lambda _: {'color':'#146985','weight':3,'fillColor':'#43a5b0','fillOpacity':.12},tooltip='Official planning area: '+boundary['name']).add_to(m)
    for point in points:
        units='Not reported' if point['units'] is None else str(point['units'])
        folium.CircleMarker(location=[point['lat'],point['lon']],radius=5,weight=1,color='#234b64',fill=True,fill_color='#d89537',fill_opacity=.85,tooltip=f"{point['name']} | Reported affordable units: {units}").add_to(m)
    folium.Marker([lat,lon],tooltip=selected+' reference point').add_to(m)
    st_folium(m,height=470,use_container_width=True,key='v201_planning_map',returned_objects=[])
    return len(points),missing

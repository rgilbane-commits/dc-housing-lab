"""Interactive teaching map. Approximate neighborhood centers, not parcel data."""
import math
import folium
from streamlit_folium import st_folium

NEIGHBORHOOD_CENTERS = {
    "Friendship Heights / Ward 3": (38.9593, -77.0847),
    "Columbia Heights / Ward 1": (38.9289, -77.0327),
    "Congress Heights / Ward 8": (38.8437, -76.9889),
    'Downtown / Ward 2': (38.8987,-77.028),
    'Takoma / Ward 4': (38.9734,-77.0171),
    'Brookland / Ward 5': (38.9323,-76.995),
    'Capitol Hill / Ward 6': (38.8864,-76.9958),
    'Deanwood / Ward 7': (38.8995,-76.9277),
    'Dupont Circle / Ward 2': (38.9096,-77.0434),
    'Navy Yard / Ward 6': (38.874,-77.001),
}

def nearest_neighborhood(coords, tolerance_km=0.7):
    if not coords or not isinstance(coords, dict):
        return None
    try:
        lat, lon = float(coords['lat']), float(coords['lng'])
    except (KeyError, TypeError, ValueError):
        return None
    nearest = min(NEIGHBORHOOD_CENTERS, key=lambda k: distance_km(lat,lon,*NEIGHBORHOOD_CENTERS[k]))
    return nearest if distance_km(lat,lon,*NEIGHBORHOOD_CENTERS[nearest]) <= tolerance_km else None

def distance_km(lat1, lon1, lat2, lon2):
    r=6371.0
    a=math.sin(math.radians(lat2-lat1)/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return r*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

def render_map(selected):
    m=folium.Map(location=[38.9072,-77.034],zoom_start=11,tiles='OpenStreetMap',control_scale=True)
    for name,(lat,lon) in NEIGHBORHOOD_CENTERS.items():
        folium.CircleMarker(location=[lat,lon],radius=12 if name==selected else 10,
            color='#102a43' if name==selected else '#167d91',weight=3,
            fill=True,fill_color='#00a89a' if name==selected else '#277fa3',fill_opacity=0.85,
            tooltip=f'{name} — click to select',popup=folium.Popup(name,max_width=320)).add_to(m)
    return st_folium(m,height=380,use_container_width=True,key='dc_interactive_map',
                     returned_objects=['last_object_clicked'])

from pathlib import Path
import ast
import sys, types
sys.modules.setdefault("streamlit_folium",types.SimpleNamespace(st_folium=lambda *a,**k: None))
from neighborhood_map import NEIGHBORHOOD_CENTERS, nearest_neighborhood, render_map

def test_no_api_key_tile_config():
    source=Path(__file__).resolve().parents[1].joinpath("neighborhood_map.py").read_text()
    assert "tiles='OpenStreetMap'" in source
    assert "Mapbox" not in source and "CartoDB" not in source
    assert "api_key" not in source

def test_render_map_with_mocked_folium(monkeypatch):
    import neighborhood_map as nm
    class MockMap:
        def __init__(self,**kw): self.kw=kw
    class MockMarker:
        def __init__(self,**kw): pass
        def add_to(self,m): return self
    monkeypatch.setattr(nm.folium,'Map',MockMap)
    monkeypatch.setattr(nm.folium,'CircleMarker',MockMarker)
    monkeypatch.setattr(nm.folium,'Popup',lambda *args,**kwargs: None)
    monkeypatch.setattr(nm,'st_folium',lambda m,**kw: {'map_kwargs':m.kw, 'callback_kwargs':kw})
    result=render_map(next(iter(NEIGHBORHOOD_CENTERS)))
    assert result['map_kwargs']['tiles']=='OpenStreetMap'
    assert result['callback_kwargs']['returned_objects']==['last_object_clicked']

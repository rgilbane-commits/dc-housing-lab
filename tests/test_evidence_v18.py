from evidence import PLANNING_AREAS, planning_area_context, district_production, records
from model import NEIGHBORHOODS, neighborhood_inputs, analyze

def test_areas_match():
    assert set(PLANNING_AREAS)==set(NEIGHBORHOODS)

def test_verified_historical_values():
    assert planning_area_context('Friendship Heights / Ward 3')['existing_2018']==470
    assert planning_area_context('Columbia Heights / Ward 1')['existing_2018']==6960
    assert planning_area_context('Congress Heights / Ward 8')['existing_2018']==15760
    assert sum(x['target_2025'] for x in PLANNING_AREAS.values() if x['target_2025'] is not None)==4120

def test_geo_period_traceability():
    for name in NEIGHBORHOODS:
        x=planning_area_context(name)
        assert x['existing_as_of']==2018 and x['target_document_year']==2019
        assert x['area'] != name and x['source_url'].startswith('https://')

def test_city_metric_asof():
    assert district_production()['delivered_units']==36216
    assert district_production()['as_of']=='2024-07-29'

def test_source_register():
    assert len(records())>=5
    assert len(set(r['id'] for r in records()))==len(records())
    assert all(r['url'].startswith('https://') and r['observation_period'] and r['geography'] for r in records())

def test_no_effect_on_underwriting():
    name='Friendship Heights / Ward 3'
    p=neighborhood_inputs(name,'Base case') if 'Base case' in __import__('model').PRESETS else neighborhood_inputs(name,list(__import__('model').PRESETS)[0])
    a=analyze(p)
    planning_area_context(name)
    assert analyze(p)==a

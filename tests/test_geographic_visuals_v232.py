from geographic_visuals import qualified_chart_rows, area_quality_summary, map_marker_legend
from live_data import DataUnavailable
import pytest

def sample(**kwargs):
    a={'area':'Mid-City','projects':3,'production_rows':3,'preservation_rows':3,'production_units_reported':120,'preservation_units_reported':40,'fully_classified':True,'inconsistent_rows':0}
    a.update(kwargs);return a

def test_fully_classified_charts():
    a=qualified_chart_rows([sample()])[0]
    assert a['Reported production']==120 and a['Reported preservation']==40

def test_partial_not_rendered_as_zero():
    a=qualified_chart_rows([sample(production_rows=2,fully_classified=False)])[0]
    assert a['Reported production'] is None and a['Reported preservation'] is None

def test_inconsistent_suppressed():
    a=qualified_chart_rows([sample(inconsistent_rows=1)])[0]
    assert a['Reported production'] is None

def test_quality_report():
    a=area_quality_summary(sample(production_rows=2,fully_classified=False))
    assert a['Comparison eligible']=='No' and a['Production field coverage']=='2/3'

def test_bad_quality_counts_rejected():
    with pytest.raises(DataUnavailable):area_quality_summary(sample(production_rows=4))

def test_legend_disclaims_inventory():
    assert 'not a current affordable housing inventory' in map_marker_legend()

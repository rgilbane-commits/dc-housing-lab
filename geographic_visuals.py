"""Presentation-only helpers for qualified planning-area GIS outputs (v2.3.2)."""
from live_data import DataUnavailable

def qualified_chart_rows(areas):
    """Never render incomplete production/preservation counts as comparable bars."""
    rows=[]
    for a in areas:
        good=bool(a.get('fully_classified')) and a.get('inconsistent_rows') == 0
        rows.append({'Planning area':a['area'],
                     'Reported production':a.get('production_units_reported') if good else None,
                     'Reported preservation':a.get('preservation_units_reported') if good else None})
    return rows

def area_quality_summary(area):
    total=area['projects']
    prod=area['production_rows']
    pres=area['preservation_rows']
    if any(type(v) is not int or v<0 for v in (total,prod,pres)) or prod>total or pres>total:
        raise DataUnavailable('Invalid area completeness counts')
    return {'Planning area':area['area'],
            'Projects':total,
            'Production field coverage':f'{prod}/{total}',
            'Preservation field coverage':f'{pres}/{total}',
            'Comparison eligible':'Yes' if area['fully_classified'] and not area['inconsistent_rows'] else 'No'}

def map_marker_legend():
    return 'Map layers: official planning-area polygon · GIS project locations · illustrative neighborhood reference point. Points are not a current affordable housing inventory.'

"""Evidence-led geographic comparisons. Never infer denominators or net new housing."""
from dataclasses import dataclass
from typing import Optional
import math
from live_data import clean_count, DataUnavailable

STATUS_PRODUCTION=('NEW CONSTRUCTION','NEW','PRODUCTION','NEW DEVELOPMENT')
STATUS_PRESERVATION=('PRESERVATION','PRESERVED','REHABILITATION','REHAB')

def classify_project(row):
    """Field-based classification: recorded production/preservation unit fields, not project STATUS_PUBLIC."""
    prod=clean_count(row.get('AFFORDABLE_UNITS_PRODUCTION'))
    pres=clean_count(row.get('AFFORDABLE_UNITS_PRESERVED'))
    total=clean_count(row.get('TOTAL_AFFORDABLE_UNITS'))
    if prod is not None and pres is not None:
        if total is not None and prod+pres>total: return {'classification':'inconsistent','production':None,'preservation':None,'total':total}
        label='mixed' if prod and pres else 'production' if prod else 'preservation' if pres else 'zero_reported'
        return {'classification':label,'production':prod,'preservation':pres,'total':total}
    if prod is not None and prod>0 and pres is None:
        return {'classification':'partial_production','production':prod,'preservation':None,'total':total}
    if pres is not None and pres>0 and prod is None:
        return {'classification':'partial_preservation','production':None,'preservation':pres,'total':total}
    return {'classification':'unclassified','production':prod,'preservation':pres,'total':total}

def analyze_area(gis):
    rows=gis.get('rows',[])
    if gis.get('status') not in ('live_verified','verified_zero') or len(rows)!=gis.get('expected_count'):
        raise DataUnavailable('Project dataset is not count-reconciled.')
    entries=[classify_project(r) for r in rows]
    inconsistent=sum(x['classification']=='inconsistent' for x in entries)
    classifications={name:sum(x['classification']==name for x in entries) for name in ('production','preservation','mixed','partial_production','partial_preservation','unclassified','zero_reported','inconsistent')}
    production=sum(x['production'] for x in entries if x['production'] is not None and x['classification']!='inconsistent')
    preservation=sum(x['preservation'] for x in entries if x['preservation'] is not None and x['classification']!='inconsistent')
    production_rows=sum(x['production'] is not None and x['classification']!='inconsistent' for x in entries)
    preservation_rows=sum(x['preservation'] is not None and x['classification']!='inconsistent' for x in entries)
    return {'area':gis['area'],'projects':len(rows),'production_units_reported':production,'preservation_units_reported':preservation,
            'production_rows':production_rows,'preservation_rows':preservation_rows,'classification_counts':classifications,
            'inconsistent_rows':inconsistent,'fully_classified':production_rows==len(rows) and preservation_rows==len(rows) and inconsistent==0,
            'retrieved_at':gis.get('retrieved_at'),'source_status':gis['status']}

def normalize_units(units,denominator,denominator_source=None,denominator_year=None):
    """Only use denominators identified by an explicit source and year."""
    if denominator is None or not denominator_source or not denominator_year:
        return None
    if isinstance(denominator,bool) or not isinstance(denominator,(int,float)) or not math.isfinite(denominator) or denominator<=0:
        return None
    if units is None or isinstance(units,bool) or not isinstance(units,(int,float)) or units<0 or not math.isfinite(units):return None
    return 1000*units/denominator

def comparison_rows(results,denominators=None):
    out=[];denominators=denominators or {}
    for result in results:
        if result is None:continue
        a=analyze_area(result)
        d=denominators.get(a['area'],{})
        val=normalize_units(a['production_units_reported'],d.get('households'),d.get('source'),d.get('year')) if a['fully_classified'] else None
        out.append({'Planning area':a['area'],'Projects (2015+ GIS layer)':a['projects'],
                    'Reported production units':a['production_units_reported'] if a['fully_classified'] else None,
                    'Reported preserved units':a['preservation_units_reported'] if a['preservation_rows']==a['projects'] and not a['inconsistent_rows'] else None,
                    'Production per 1,000 households':round(val,2) if val is not None else None,
                    'Unclassified/partial/inconsistent records':a['projects']-a['classification_counts']['production']-a['classification_counts']['preservation']-a['classification_counts']['mixed']-a['classification_counts']['zero_reported'],
                    'Retrieved UTC':a['retrieved_at'],'Data qualification':'Complete breakdown' if a['fully_classified'] else 'Partial: do not interpret production/preservation as complete totals'})
    return out

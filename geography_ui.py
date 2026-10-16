"""Presentation-only helpers. Never substitute neighborhood reference points for ward statistics."""
import re
from evidence import planning_area_context

def ward_number(name):
    match = re.search(r"/ Ward ([1-8])$", name)
    if not match:
        raise ValueError(f"No valid ward reference in {name!r}")
    return int(match.group(1))

def sorted_reference_locations(locations):
    return sorted(locations, key=lambda n: (ward_number(n), n.split(" / Ward ")[0].casefold()))

def area_rows(locations):
    by_area={}
    for location in locations:
        context=planning_area_context(location)
        area=context['area']
        if area in by_area:
            existing=by_area[area]
            if (existing['Existing affordable units (2018)']!=context['existing_2018'] or
                existing['Goal for additional units by 2025 (set 2019)']!=context['target_2025']):
                raise ValueError(f"Conflicting source observations for planning area {area}")
            continue
        by_area[area]={
            'DC planning area':area,
            'Existing affordable units (2018)':context['existing_2018'],
            'Goal for additional units by 2025 (set 2019)':context['target_2025'],
        }
    return [by_area[area] for area in sorted(by_area,key=str.casefold)]

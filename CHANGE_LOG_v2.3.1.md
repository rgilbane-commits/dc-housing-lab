# v2.3.1 Change Log

- Added `scenario_compare.py`, an independent comparison adapter that consumes immutable snapshots of allocation lines and financing controls.
- Added A/B scenario capture, side-by-side metric table, comparative bar charts for potential and screened homes, geography and strategy allocation, and CSV export under Investment Strategy.
- Added four regression tests for snapshot integrity, budget enforcement, delta reconciliation, and malformed captures.
- All 11 principal computational modules listed in the QA report are byte-identical to v2.3.0.
- Scenario snapshots reside in Streamlit session state; they do not persist across browser sessions or revisions.

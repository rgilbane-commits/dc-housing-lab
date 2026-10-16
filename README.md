# DC Housing Lab v2.3.1 — Investment Strategy Visualization

## Deployment
Unzip and upload the application files to the existing GitHub Streamlit repository, replacing matching files, including `app.py`, `scenario_compare.py` and the new test file. Keep the project's Streamlit entry point as `app.py`. Dependencies are unchanged.

## Usage
Open **Investment Strategy**. Allocate grants to DC planning areas/strategies and select funding assumptions. Below the financial screening table, enter a scenario label and select **Save as Scenario A**. Change inputs and select **Save as Scenario B**. Compare the metric table and three bar charts or download the A/B CSV. To begin again, use **Clear saved scenarios**.

## Interpretation
All allocations and public support per home are illustrative. 'Potential homes' are mathematical capacity under user-selected subsidy assumptions; 'passing financial screen' means a hypothetical underwriting archetype passed automated tests, **not** a development approval. Delivered homes always remain zero. A/B snapshots are session-only.

## Quality control
See `QA_AUDIT_REPORT_v2.3.1.md` and `SHA256_MANIFEST_v2.3.1.txt`. Browser QA is required before production acceptance.

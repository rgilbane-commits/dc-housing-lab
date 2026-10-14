# DC Housing Lab v1.3 — Streamlit Classroom Edition

Interactive Washington, DC affordable-housing classroom simulation. All location-level numbers are illustrative only.

## New in v1.3
- **Stress test & compare tab:** 3×3 development-cost / capitalization-rate sensitivity, minimum total grant required for the model's margin test, A/B comparison and CSV download.
- **Reality Check sidebar:** selectable development event: construction cost increase, cap-rate increase, lower permitted density, reduced grant funding.
- **Explain the economics:** student-facing descriptions of NOI, cap rates, AMI, margin gaps and grants versus loans.
- **Number formatting preserved:** currencies keep signs and commas; percentages and unit quantities receive different display formats. Numerical CSV values remain numeric.

## Cloud deployment
1. Extract the ZIP. Upload the contents of this folder—not the ZIP itself—to the root of your existing GitHub repository.
2. Commit `Upgrade DC Housing Lab to v1.3` on the branch used by Streamlit Community Cloud.
3. Confirm `app.py`, `model.py`, `classroom.py`, `display_format.py`, `upgrade.py`, `requirements.txt` are at repository root.
4. Open your Streamlit app. Verify its header shows `CLASSROOM EDITION v1.3`.
5. Run the smoke tests in `QA_AUDIT_REPORT_v1.3.md`. For failed deployment inspect **Manage app → Logs**.

## Run locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Automated QA
```bash
python -m unittest discover -s tests -v
```

## Model caution
The screening metric capitalizes NOI after modeled public-loan payments, then compares property value plus grant support against cost plus a classroom margin. This is not conventional lender sizing, underwriting, AMI/rent limit certification, IRR or an entitlement determination. All affordability and DC neighborhood assumptions are hypothetical.

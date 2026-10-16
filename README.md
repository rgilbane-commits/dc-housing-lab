# DC Housing Lab v2.2.1 — Investment Feasibility Integration

## Deployment
Upload the contents of this folder (not its parent directory) to the `main` branch of your existing Streamlit Cloud GitHub repository. The entry point remains `app.py`. Ensure `investment_feasibility.py` is uploaded. No API keys are required for the new tab; previous Census settings are unchanged.

## New capability
In **Public investment strategy**, set allocations by planning area and strategy. Under **Project-level feasibility screening**, adjust requested private debt as a percentage of modeled development cost, committed equity as a percentage of cost, and reserve allowance as a share of NOI. Download the resulting CSV.

The screen uses existing `model.Inputs` and `model.analyze` calculations, with explicit **illustrative** project archetypes defined in `investment_feasibility.py`. Each allocation line is treated as a hypothetical standalone project. Its grant is the whole-home portion of the allocation; any fractional remainder is shown as uncommitted. A line above 2,000 modeled homes is excluded from project underwriting rather than silently split into multiple projects.

### Three distinct outcomes
* **Potential homes:** integer illustrative unit capacity using allocation / assumed per-home public support.
* **Screened homes:** potential units whose *illustrative* economic margin, funding, and operating screens all pass; not a qualified real transaction.
* **Delivered homes:** always zero, as project completion cannot be determined from these inputs.

### Core screen logic
The financial test uses the existing unlevered value / cost and developer-margin test; private debt sizing respects modeled LTV, LTC, and DSCR limits; residual equity is compared to modeled committed equity; post-reserve cash flow is compared to debt service. The model does NOT verify parcel, title, zoning, subsidy award, funding commitments, construction costs, project eligibility, investment covenants, preservation transaction outcomes, or actual project delivery. Strategy archetype pricing and unit mixes are fictional, not live DC evidence. Preservation uses an illustrative acquisition-and-rehab cost multiplier, not construction economics.

### Source of truth and QA
All prior v2.2.0 modules retained; the new feasibility module imports `analyze()` rather than reimplementing the finance math. Run `python -m pytest -q` from repository root. See `QA_AUDIT_REPORT_v2.2.1.md` and `CHANGE_LOG_v2.2.1.md`. Streamlit browser smoke test remains a deployment acceptance item.

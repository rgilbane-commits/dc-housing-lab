# DC Housing Lab v2.4.2 — Financial Margin Remediation QA

## Definitions

* Legacy total-cost grant-offset margin gap (signed): `C*(1+m)-G-V`. Retained in `economic_gap` / `margin_gap` for backwards compatibility and classroom scoring. This is **not** a financing funding gap, developer profit, or equity IRR.
* Unsubsidized value-cost spread: `V-C` (and optional percentage of net cost). Does not assume a grant.
* Conditional net-cost margin gap: `max(0,C-min(G,C))*(1+m)-V`; assumes grants are allowed to offset eligible project cost. Eligibility **has not been verified**; any excess grant is identified separately, not treated as developer profit.
* Financing separately represented by required equity, debt support tests, and excess capital sources.

Existing underwriting, debt sizing and classroom scoring formulas are preserved; metrics and presentation are disambiguated. Different policy grant covenants can change actual economic entitlements. Public loans are not counted as grants.

## Controls

Automated regression and new independent arithmetic examples executed. Any obsolete hash-pinning assertions replaced with behavioral invariants; original `upgrade.py` restored unchanged. No authenticated browser session or live GIS / Census verification performed. Release remains **conditional**.

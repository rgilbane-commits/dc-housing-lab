# DC Housing Lab v1.3 — QC / Audit Report

**Disposition:** PASS WITH LIMITATIONS for source delivery; live deployment acceptance is pending.

## Verified
- 38 automated unittest cases passed (28 retained plus 10 new).
- Syntax compiled for application and support modules.
- v1.2.1 density/land/grant button callback protections were retained.
- Sensitivity table center cell exactly reproduces the baseline margin gap.
- Sensitivity results move in the expected direction when development costs or cap rates rise.
- Grant requirement closes the simplified margin gap under tested inputs.
- A/B scenario capture retains underlying numeric fields, keeps scenario inputs, and exports CSV.
- All displayed sensitivity/comparison dollar figures use the sign-preserving money formatter, with percent and integer formatting applied to respective columns.
- Streamlit widget updates for Reality Check are performed in a callback before slider instantiation.

## Material limitations / residual risks
1. **Not verified in a running Streamlit browser**: Streamlit is not installed in this execution environment. The hosted GitHub/Streamlit deployment must be tested for real UI behavior.
2. Financial forecasts use classroom teaching assumptions, not observed or current DC market metrics. This is not underwriting or program compliance advice.
3. Cost shock snaps to the next closest $25,000 per apartment to match the current cost slider's increments. Density shock snaps to the closest 10 apartments. Grant shock snaps to the nearest $1M. Hence percentage shocks are approximate.
4. "Minimum grant" is a mathematical requirement for the simplified value-over-cost margin test, not an amount a government funding program would award.
5. A/B scenarios are saved in an individual Streamlit browser session and are not multi-user synchronized.
6. The model's loan residual-value approach is a classroom proxy, not conventional full project debt sizing or IRR underwriting.

## Hosted smoke test before class
1. Load v1.3 and confirm all seven tabs render.
2. Apply each Reality Check type; verify the selected slider changes and no `StreamlitWidgetAlreadyInstantiatedError` occurs.
3. Save Scenario A, change assumptions, save B, compare results and export CSV.
4. Verify the sensitivity table and minimum required grant update with changing cost and cap rate.
5. Re-test existing density bonus, public land contribution and grant buttons.
6. Confirm negative gaps show a minus sign and numeric formatting is legible on laptop and projector.

# DC Housing Lab v2.7.0 — Development Returns & Capital Structure

- Added a monthly construction-to-sale equity ledger and a dashboard within the existing ten-year outlook.
- Construction phase: straight-line development spending, staged grant and construction debt draws, monthly interest carry paid by equity, and upfront construction loan fee.
- Stabilization: permanent and public financing takeout, construction loan retirement, private loan origination fee and net proceeds/shortfall to equity.
- Operating phase: illustrative NOI ramp, monthly replacement reserves, and amortizing private/public debt service.
- Disposition: forward NOI capitalization, sale costs, outstanding loan repayments, dated monthly equity cash flows, equity multiple and annualized levered IRR.
- Visualization: financing-balance timeline, monthly net equity cash-flow bars, 5x5 cap-rate/construction-cost IRR sensitivity grid, monthly ledger CSV.
- New tests reconcile uses and sources, sale proceeds, ledger cash flows, cap/rate sensitivity and infeasible scenarios.
- Existing `model.py` and `forecast.py` have NOT been modified.

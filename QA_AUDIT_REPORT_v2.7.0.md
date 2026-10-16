# DC Housing Lab v2.7.0 — Builder QA report

**Disposition: CONDITIONAL / NOT INDEPENDENTLY APPROVED.**

## Verification
- 265 automated tests passed, including 8 new monthly-returns tests.
- Python source compilation passed.
- Monthly source/use and completion-period debt-takeout identities independently asserted.
- Construction balances, interest carry, disposition debt paydown, equity cash-flow arrays, and exit capitalization reconciled.
- Debt, operating and exit assumptions use the existing `model.analyze` result; changes to `model.py` and `forecast.py` are out of scope.

## High-priority limitations, not closed
1. **Live browser unverified:** Streamlit/plot rendering, state preservation, download clicks and responsive layout require authenticated testing.
2. **Simplified construction:** All development spending and public grant are drawn pro-rata, not a trade-based schedule; the construction loan is funded proportionally, with monthly accrued interest paid by equity rather than capitalized into debt.
3. **Takeout assumption:** Permanent private and public debt are modeled as fully available at completion at the existing debt capacities. This is not a verified construction-to-permanent commitment, nor is refinance timing or escrow modeled.
4. **Lease-up simplification:** Stabilized monthly NOI is multiplied by linear lease-up. Actual fixed expenses, concessions, staggered deliveries, and reserve funding can materially alter deficits.
5. **IRR and equity multiple:** Monthly equity cash flows include investment and proceeds. Multiple uses positive/negative cash-flow sums, not preferred return or promote waterfalls. IRR uses a bracketing solver; non-conventional cash flows can have multiple valid IRRs or no uniquely meaningful IRR. Do not interpret as a fund investor return.
6. **Missing components:** Income taxes, LIHTC timing, commercial operations, deferred developer fee, balloon/refinancing covenants, retained reserves, debt release prices, financing fees beyond entered inputs and capital markets execution are excluded.
7. **Comparability:** The ten-year forecast assumes full equity at inception while the new monthly model stages cash flows; the two IRRs are not directly comparable.
8. **Funding risk:** When model shows additional equity needed, the return is conditional on that equity being supplied. Staged sources are instructional, not proof of feasibility.

## Acceptance before baseline freeze
- Confirm no Streamlit widget key collisions and charts render on desktop and projector widths.
- Run default, no-grant, zero construction loan, failed public DSCR, and over-advance cases.
- Compare exported ledger totals with visible KPIs and month-by-month financing.
- Exercise cap-rate/cost sensitivity matrix at its boundaries.

import pytest
from model import Inputs, analyze
from development_returns import DevelopmentAssumptions, calculate, _irr_roots, _irr


def test_multiple_irr_not_misreported():
    # -100, +230, -132 admits roots 10% and 20% per period.
    roots = _irr_roots([-100, 230, -132])
    assert len(roots) == 2
    assert roots[0] == pytest.approx(.1, abs=1e-6)
    assert roots[1] == pytest.approx(.2, abs=1e-6)
    assert _irr([-100, 230, -132]) is None


def test_single_irrs_and_unavailable():
    assert _irr([-100, 110]) == pytest.approx(.1)
    assert _irr([-100, -10]) is None


def test_operating_deficits_reconcile_to_ledger():
    p = Inputs()
    r = analyze(p)
    a = DevelopmentAssumptions(leaseup_months=36)
    result = calculate(p, r, a)
    rows = [x for x in result['rows'] if x['phase'] == 'Operations']
    # The final operating-month row includes sale proceeds; reconstruct operating cash flow.
    deficits = []
    for x in rows:
        cash = x['net_equity_cash_flow'] - (result['net_sale_to_equity'] if x is rows[-1] and result['net_sale_to_equity'] is not None else 0)
        if cash < 0:
            deficits.append(-cash)
    assert result['operating_deficit_total'] == pytest.approx(sum(deficits))
    assert result['operating_deficit_months'] == len(deficits)


def test_refinance_equity_sources():
    p = Inputs()
    r = analyze(p)
    result = calculate(p, r)
    assert result['refinance_equity_call'] == pytest.approx(max(0, -result['net_permanent_financing_proceeds']))
    assert result['refinance_equity_distribution'] == pytest.approx(max(0, result['net_permanent_financing_proceeds']))
    assert result['irr_root_count'] >= 0

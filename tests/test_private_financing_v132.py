import unittest
from dataclasses import replace
from model import Inputs, analyze
class TestPermanentDebt(unittest.TestCase):
    def test_borrowing_does_not_change_unlevered_value(self):
        a=analyze(Inputs(private_debt_m=0)); b=analyze(Inputs(private_debt_m=60))
        self.assertEqual(a['stabilized_value'],b['stabilized_value'])
        self.assertEqual(a['economic_gap'],b['economic_gap'])
    def test_requested_private_debt_capped(self):
        r=analyze(Inputs(private_debt_m=1000))
        self.assertAlmostEqual(r['funded_private_debt'],r['private_debt_capacity'])
        self.assertTrue(r['private_debt_shortfall']>0)
    def test_zero_private_and_public_no_dscr(self):
        r=analyze(Inputs(private_debt_m=0,loan_m=0))
        self.assertIsNone(r['total_dscr'])
        self.assertEqual(r['private_annual_debt_service'],0)
    def test_loan_service_adds(self):
        r=analyze(Inputs(private_debt_m=20,loan_m=4))
        self.assertAlmostEqual(r['total_annual_debt_service'],r['private_annual_debt_service']+r['annual_public_loan_payment'])
        self.assertAlmostEqual(r['total_dscr'],r['noi']/r['total_annual_debt_service'])
    def test_public_loan_crowds_out_private_dscr_capacity(self):
        a=analyze(Inputs(loan_m=0)); b=analyze(Inputs(loan_m=20))
        self.assertLessEqual(b['private_debt_by_dscr'],a['private_debt_by_dscr'])
    def test_higher_rate_reduces_dscr_capacity(self):
        a=analyze(Inputs(private_rate_pct=4)); b=analyze(Inputs(private_rate_pct=9))
        self.assertLess(b['private_debt_by_dscr'],a['private_debt_by_dscr'])
    def test_ltv_ltc_bind(self):
        x=analyze(Inputs(max_private_ltv_pct=0,max_private_ltc_pct=70))
        self.assertEqual(x['private_debt_capacity'],0)
        y=analyze(Inputs(max_private_ltv_pct=75,max_private_ltc_pct=0))
        self.assertEqual(y['private_debt_capacity'],0)
    def test_equity_gap_reconciles(self):
        r=analyze(Inputs(private_debt_m=30,committed_equity_m=12))
        self.assertAlmostEqual(r['equity_required'],max(0,r['net_cost']-r['grant']-r['loan']-r['funded_private_debt']))
        self.assertAlmostEqual(r['additional_equity_needed'],max(0,r['equity_required']-r['committed_equity']))
    def test_more_equity_does_not_change_capacity(self):
        a=analyze(Inputs(committed_equity_m=0));b=analyze(Inputs(committed_equity_m=60))
        self.assertEqual(a['private_debt_capacity'],b['private_debt_capacity'])
    def test_zero_interest_support(self):
        r=analyze(Inputs(private_rate_pct=0))
        self.assertGreater(r['private_debt_capacity'],0)
    def test_bad_assumptions(self):
        for change in (dict(min_total_dscr=.8),dict(max_private_ltv_pct=101),dict(private_amort_years=0)):
            with self.assertRaises(ValueError):analyze(replace(Inputs(),**change))
    def test_no_negative_loan(self):
        with self.assertRaises(ValueError): analyze(Inputs(private_rate_pct=-1))
if __name__=='__main__':unittest.main()

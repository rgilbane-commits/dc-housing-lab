import unittest
from dataclasses import replace
from model import Inputs, analyze
from upgrade import sensitivity, minimum_grant_to_margin
class FinancingCorrections(unittest.TestCase):
    def test_loan_no_impact_on_unlevered_value_or_margin(self):
        a,b=analyze(Inputs(loan_m=0)),analyze(Inputs(loan_m=10))
        self.assertEqual(a['stabilized_value'],b['stabilized_value'])
        self.assertEqual(a['economic_gap'],b['economic_gap'])
    def test_loan_reduces_funding_gap(self):
        a,b=analyze(Inputs(loan_m=0)),analyze(Inputs(loan_m=10))
        self.assertAlmostEqual(a['capital_stack_gap']-b['capital_stack_gap'],10e6)
        self.assertGreater(b['annual_public_loan_payment'],0)
    def test_grant_improves_both_gaps(self):
        a,b=analyze(Inputs(grant_m=0)),analyze(Inputs(grant_m=10))
        for metric in ('economic_gap','capital_stack_gap'):
            self.assertAlmostEqual(a[metric]-b[metric],10e6)
    def test_equity_and_private_debt_are_sources_not_value(self):
        a=analyze(Inputs(private_debt_m=0,committed_equity_m=0))
        b=analyze(Inputs(private_debt_m=10,committed_equity_m=5))
        self.assertEqual(a['economic_gap'],b['economic_gap'])
        self.assertAlmostEqual(a['capital_stack_gap']-b['capital_stack_gap'],15e6)
    def test_coverage_public_only(self):
        x=analyze(Inputs(loan_m=10))
        self.assertAlmostEqual(x['public_loan_dscr'],x['noi']/x['annual_public_loan_payment'])
        self.assertIsNone(analyze(Inputs(loan_m=0))['public_loan_dscr'])
    def test_economic_sensitivity_not_affected_by_loan(self):
        self.assertEqual(sensitivity(Inputs(loan_m=0)),sensitivity(Inputs(loan_m=10)))
        self.assertEqual(minimum_grant_to_margin(Inputs(loan_m=0)),minimum_grant_to_margin(Inputs(loan_m=10)))
    def test_grant_and_loan_same_initial_capital_different_margin(self):
        grant=analyze(Inputs(grant_m=10,loan_m=0));loan=analyze(Inputs(grant_m=0,loan_m=10))
        self.assertAlmostEqual(grant['capital_stack_gap'],loan['capital_stack_gap'])
        self.assertAlmostEqual(loan['economic_gap']-grant['economic_gap'],10e6)
    def test_no_negative_financing_inputs(self):
        for field in ('private_debt_m','committed_equity_m'):
            with self.assertRaises(ValueError): analyze(replace(Inputs(),**{field:-1}))
if __name__=='__main__':unittest.main()

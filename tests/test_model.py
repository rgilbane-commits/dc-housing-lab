import unittest
from dataclasses import replace
from model import Inputs, analyze, optimal_subsidy_m

class ModelTests(unittest.TestCase):
    def test_baseline_counts_and_arithmetic(self):
        r = analyze(Inputs())
        self.assertEqual(r['affordable_units'], 60)
        self.assertEqual(r['market_units'], 140)
        self.assertAlmostEqual(r['gross_revenue'], 6120000)
        self.assertAlmostEqual(r['noi'], 3414960)
        self.assertAlmostEqual(r['gross_tdc'], 90000000)
        self.assertAlmostEqual(r['funding_gap'], 90000000-15000000-3414960/.055)

    def test_more_affordability_decreases_value(self):
        a = analyze(Inputs(affordable_pct=0))
        b = analyze(Inputs(affordable_pct=100))
        self.assertGreater(a['stabilized_value'], b['stabilized_value'])

    def test_subsidy_does_not_change_noi(self):
        a=analyze(Inputs(subsidy_m=0))
        b=analyze(Inputs(subsidy_m=25))
        self.assertEqual(a['noi'],b['noi'])
        self.assertAlmostEqual(a['funding_gap']-b['funding_gap'],25000000)

    def test_required_subsidy_closes_gap(self):
        p=Inputs()
        s=optimal_subsidy_m(p)
        self.assertAlmostEqual(analyze(replace(p,subsidy_m=s))['funding_gap'],0,places=5)

    def test_full_affordable_zero_market(self):
        r=analyze(Inputs(affordable_pct=100))
        self.assertEqual(r['market_units'],0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): analyze(Inputs(cap_rate_pct=0))
        with self.assertRaises(ValueError): analyze(Inputs(affordable_pct=110))

    def test_land_credit_not_cash_and_parking_cost(self):
        r=analyze(Inputs(public_land_credit_m=5,parking_cost_per_space=20000))
        self.assertAlmostEqual(r['parking_increment'],200*0.5*20000)
        self.assertAlmostEqual(r['land_credit'],5000000)
        self.assertAlmostEqual(r['net_tdc'],87000000)

if __name__=='__main__': unittest.main()

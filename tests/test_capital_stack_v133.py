import unittest
from dataclasses import replace
from model import Inputs, analyze
from capital_stack import breakdown, visual

class StackTests(unittest.TestCase):
    def test_basic_reconciles(self):
        d=breakdown(analyze(Inputs()))
        self.assertAlmostEqual(sum(v for _,v in d['allocated']),d['cost'],places=4)
        self.assertAlmostEqual(d['net_gap'],d['cost']-d['available_total'])
    def test_shortfall_matches_model(self):
        r=analyze(Inputs())
        d=breakdown(r)
        self.assertAlmostEqual(d['shortfall'],r['additional_equity_needed'])
    def test_private_capacity_not_requested(self):
        r=analyze(replace(Inputs(),private_debt_m=100, max_private_ltv_pct=5))
        d=breakdown(r)
        self.assertEqual(dict(d['sources'])['Private loan'],r['funded_private_debt'])
        self.assertLess(r['funded_private_debt'],r['private_debt'])
    def test_public_loan_increases_sources(self):
        a=breakdown(analyze(replace(Inputs(),loan_m=0)))
        b=breakdown(analyze(replace(Inputs(),loan_m=10)))
        self.assertAlmostEqual(b['available_total']-a['available_total'],10e6+dict(b['sources'])['Private loan']-dict(a['sources'])['Private loan'])
    def test_overfunding_is_reported(self):
        r=analyze(replace(Inputs(),units=50,grant_m=100,loan_m=50,committed_equity_m=100))
        d=breakdown(r)
        self.assertEqual(d['shortfall'],0)
        self.assertGreater(d['unused_sources'],0)
        self.assertAlmostEqual(sum(x for _,x in d['allocated']),d['cost'])
    def test_zero_sources(self):
        r=analyze(replace(Inputs(),grant_m=0,loan_m=0,private_debt_m=0,committed_equity_m=0))
        d=breakdown(r)
        self.assertEqual(d['shortfall'],d['cost'])
    def test_landing_credit_reduces_uses(self):
        a=breakdown(analyze(Inputs()))
        b=breakdown(analyze(replace(Inputs(),land_credit_m=10)))
        self.assertAlmostEqual(a['cost']-b['cost'],10e6)
    def test_chart_has_labels(self):
        s=visual(analyze(Inputs()),lambda x:f'${x:,.0f}')
        self.assertIn('NET DEVELOPMENT COST',s)
        self.assertIn('Additional equity needed',s)
    def test_invalid_sources(self):
        with self.assertRaises(ValueError): breakdown({'net_cost':1,'grant':-1,'loan':0,'funded_private_debt':0,'committed_equity':0})

if __name__=='__main__':unittest.main()

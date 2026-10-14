import unittest
from dataclasses import replace
from model import Inputs, analyze
from upgrade import shock, sensitivity, minimum_grant_to_margin, snapshot

class UpgradeTests(unittest.TestCase):
    def setUp(self): self.p=Inputs()
    def test_cost_shock(self): self.assertGreater(shock(self.p,'Construction cost +15%').cost_per_unit,self.p.cost_per_unit)
    def test_cap_shock(self): self.assertEqual(shock(self.p,'Cap rate +0.75 percentage points').cap_rate_pct,6.25)
    def test_density_shock(self): self.assertEqual(shock(self.p,'Allowable apartments -20%').units,160)
    def test_grant_shock(self): self.assertEqual(shock(self.p,'Grant funding reduced by half').grant_m,8)
    def test_shock_limits(self):
        self.assertLessEqual(shock(replace(self.p,cap_rate_pct=9),'Cap rate +0.75 percentage points').cap_rate_pct,9)
        self.assertGreaterEqual(shock(replace(self.p,units=50),'Allowable apartments -20%').units,50)
    def test_sensitivity_baseline(self):
        rows=sensitivity(self.p)
        self.assertEqual(len(rows),3)
        self.assertAlmostEqual(rows[1]['5.50% cap'],analyze(self.p)['margin_gap'])
    def test_sensitivity_direction(self):
        rows=sensitivity(self.p)
        self.assertGreater(rows[2]['5.50% cap'],rows[0]['5.50% cap'])
        self.assertGreater(rows[1]['6.00% cap'],rows[1]['5.00% cap'])
    def test_minimum_grant(self):
        minimum=minimum_grant_to_margin(self.p)
        self.assertLessEqual(analyze(replace(self.p,grant_m=minimum/1e6))['margin_gap'],.00001)
    def test_snapshot(self):
        s=snapshot(self.p,'Test')
        self.assertEqual(s['Homes'],200)
        self.assertEqual(s['Affordable homes'],60)
        self.assertEqual(s['inputs']['grant_m'],15)
    def test_invalid_shock(self):
        with self.assertRaises(ValueError):shock(self.p,'not a shock')

if __name__=='__main__':unittest.main()

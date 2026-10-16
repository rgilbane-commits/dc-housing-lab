import unittest
from model import Inputs, analyze
from capital_stack import breakdown
from cash_flow import annual_waterfall
from visuals import building_massing, finance_stack, waterfall_chart
from display_format import money

class VisualsTests(unittest.TestCase):
    def test_massing_extremes(self):
        for units,aff in [(50,0),(50,50),(200,60),(500,500)]:
            html=building_massing(units,aff)
            self.assertIn(f'{units:,} apartments',html)
            self.assertIn(f'Restricted {aff:,}',html)
            self.assertIn('conceptual floors',html)
    def test_invalid_massing(self):
        with self.assertRaises(ValueError): building_massing(20,21)
    def test_funding_and_waterfall_for_cases(self):
        for p in [Inputs(),Inputs(loan_m=10),Inputs(grant_m=40),Inputs(affordable_pct=100),Inputs(loan_m=50,private_debt_m=90)]:
            r=analyze(p);stack=breakdown(r);wf=annual_waterfall(r)
            html=finance_stack(stack,lambda x:money(x,compact=True))
            chart=waterfall_chart(wf,lambda x:money(x,compact=True))
            self.assertIn('Sources & uses',html)
            self.assertIn('cash flow to equity',chart)
            self.assertIn('<svg',chart)
            self.assertAlmostEqual(sum(x for _,x in stack['allocated']),stack['cost'],places=2)
    def test_source_has_no_formula_changes(self):
        from pathlib import Path
        import hashlib
        root=Path(__file__).resolve().parents[1]
        baseline={
            'capital_stack.py': 'c1551c936e7fa76bfb29cba2c32dc8961af8174281855d24286895250546801e',
            'cash_flow.py': 'cae431c60d806820dfa112e8ba2e90a2909c1671ab516c84c46431495b782204',
            'classroom.py': '72ab973f5e88d1d8ba16b3c308b8bf5818f6fe4a29068c13570428859daba54e',
            'display_format.py': '6a2f34dbfa517cc26b7d3030922cdd0c0e2855ff0c586da3b9f1aae0a78bf62d',
        }
        for name,expected in baseline.items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),expected)

    def test_financial_formulas_preserve_legacy_and_expose_new_metrics(self):
        from model import Inputs, analyze
        r=analyze(Inputs())
        assert abs(r['margin_gap']-r['legacy_total_cost_margin_gap'])<1e-6
        assert abs(r['legacy_total_cost_margin_gap']-(r['net_cost']*(1+r['return_margin_pct']/100)-r['grant']-r['stabilized_value']))<1e-5
        assert abs(r['net_cost_margin_gap']-(r['net_capital_cost_after_eligible_grant']*(1+r['return_margin_pct']/100)-r['stabilized_value']))<1e-5

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
        root=Path(__file__).resolve().parents[1]
        old=Path('/mnt/data/DC_Housing_Lab_v1.3.4')
        for name in ('model.py','capital_stack.py','cash_flow.py','upgrade.py','classroom.py','display_format.py'):
            if old.exists():self.assertEqual((root/name).read_bytes(),(old/name).read_bytes())

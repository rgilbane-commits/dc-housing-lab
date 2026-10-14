import unittest
from dataclasses import replace
from model import Inputs, analyze, annuity_payment, neighborhood_inputs, NEIGHBORHOODS, income_examples

class ModelTest(unittest.TestCase):
    def test_baseline(self):
        r=analyze(Inputs());self.assertEqual(r['restricted_units'],60);self.assertGreater(r['noi'],0)
    def test_more_affordability_reduces_value(self):
        a=analyze(Inputs(affordable_pct=10));b=analyze(Inputs(affordable_pct=80));self.assertGreater(a['stabilized_value'],b['stabilized_value'])
    def test_grant_reduces_gap_dollar_for_dollar(self):
        a=analyze(Inputs(grant_m=0));b=analyze(Inputs(grant_m=10));self.assertAlmostEqual(a['margin_gap']-b['margin_gap'],10e6)
    def test_loan_is_not_grant(self):
        a=analyze(Inputs(loan_m=0));b=analyze(Inputs(loan_m=10));self.assertAlmostEqual(b['margin_gap'],a['margin_gap']);self.assertAlmostEqual(b['grant'],a['grant']);self.assertAlmostEqual(a['capital_stack_gap']-b['capital_stack_gap'],10e6)
    def test_zero_interest_loan(self):self.assertAlmostEqual(annuity_payment(30e6,0,30),1e6)
    def test_land_cost_limited(self):
        r=analyze(Inputs(units=1,cost_per_unit=300000,land_credit_m=50));self.assertEqual(r['net_cost'],0)
    def test_no_income_loan(self):
        r=analyze(Inputs(loan_m=50,affordable_pct=100,affordable_rent=500));self.assertLess(r['public_loan_dscr'],1)
    def test_neighborhoods(self):
        for n in NEIGHBORHOODS:self.assertGreater(analyze(neighborhood_inputs(n))['gross_cost'],0)
    def test_income_budgets(self):
        t=income_examples(160000);self.assertAlmostEqual(t[0]['rent_budget'],1200)
    def test_bad_inputs(self):
        with self.assertRaises(ValueError):analyze(Inputs(cap_rate_pct=0))
if __name__=='__main__':unittest.main()

class ClassroomQA(unittest.TestCase):
    def test_building_counts_and_visual_cap(self):
        from classroom import building_html
        html=building_html(200,60)
        self.assertEqual(html.count('class="apt '),100)
        self.assertEqual(html.count('class="apt aff"'),30)
        self.assertIn('60 restricted of 200',html)
    def test_building_boundary(self):
        from classroom import building_html
        for u,a in [(1,0),(1,1),(2000,2000),(2000,0)]:
            self.assertTrue(building_html(u,a))
        with self.assertRaises(ValueError): building_html(50,51)
    def test_household_budget_utilities(self):
        from classroom import household_results
        rows=household_results(Inputs(affordable_rent=1500),utility_allowance=150)
        self.assertEqual(len(rows),4)
        teacher=rows[0]
        self.assertEqual(teacher['Rent budget after utilities ($/mo)'],1675)
        self.assertEqual(teacher['Can afford restricted rent?'],'Yes')
        self.assertEqual(rows[-1]['Can afford restricted rent?'],'No')
    def test_household_zero_budget(self):
        from classroom import household_results
        rows=household_results(Inputs(),utility_allowance=4000)
        self.assertTrue(all(x['Rent budget after utilities ($/mo)']==0 for x in rows))
    def test_invalid_household_utilities(self):
        from classroom import household_results
        with self.assertRaises(ValueError): household_results(Inputs(),utility_allowance=-1)
    def test_tradeoffs_reflect_direction(self):
        from classroom import tradeoff_messages
        base=Inputs()
        messages=tradeoff_messages(replace(base,affordable_pct=60),base)
        self.assertTrue(any('Restricted housing: +60' in m for m in messages))
        self.assertTrue(any('falls' in m for m in messages))
        self.assertTrue(any('worsens' in m for m in messages))
    def test_tradeoffs_grant_and_loan_differ(self):
        from classroom import tradeoff_messages
        base=Inputs(grant_m=0)
        grant=tradeoff_messages(replace(base,grant_m=10),base)
        loan=tradeoff_messages(replace(base,loan_m=10),base)
        self.assertTrue(any('nonrepayable' in m for m in grant))
        self.assertTrue(any('Repayable' in m for m in loan))
    def test_all_neighborhood_scenarios(self):
        from model import PRESETS
        for neighborhood in NEIGHBORHOODS:
            for preset in PRESETS:
                self.assertIsInstance(analyze(neighborhood_inputs(neighborhood,preset))['margin_gap'],float)
    def test_extreme_loan_flags_warning(self):
        from classroom import tradeoff_messages
        base=Inputs()
        loan=replace(base,loan_m=50,loan_years=10,loan_rate_pct=10)
        self.assertTrue(any('WARNING' in x for x in tradeoff_messages(loan,base)))
    def test_source_contains_all_tabs_and_safety_copy(self):
        from pathlib import Path
        app=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
        for marker in ['Instructor view','Build a project','Policy lab','Who can afford it?','Classroom challenge','building_massing(', 'household_results(', 'tradeoff_messages(','illustrative']:
            self.assertIn(marker,app)

import unittest
from dataclasses import replace
from model import Inputs,analyze
from forecast import ForecastAssumptions,project,_amortization
class ForecastTests(unittest.TestCase):
 def setUp(self):
  self.p=Inputs();self.r=analyze(self.p)
 def test_10_years(self):self.assertEqual(len(project(self.p,self.r)['rows']),10)
 def test_revenue_reconciliation(self):
  f=project(self.p,self.r)
  self.assertAlmostEqual(f['rows'][0]['scheduled_rent'],self.r['gross_rent'])
 def test_noi_reconciliation(self):
  f=project(self.p,self.r,ForecastAssumptions(vacancy_pct=self.p.vacancy_pct))
  self.assertAlmostEqual(f['rows'][0]['noi'],self.r['noi'])
 def test_cash_flow_reconciliation(self):
  f=project(self.p,self.r);x=f['rows'][0]
  self.assertAlmostEqual(x['cash_flow_to_equity'],x['noi']-x['replacement_reserve']-x['total_debt_service'])
 def test_debt_balance_declines(self):
  f=project(self.p,self.r);self.assertLess(f['rows'][-1]['private_balance'],self.r['funded_private_debt'])
 def test_loan_zero(self):self.assertEqual(_amortization(0,5,30),[(0,0)]*10)
 def test_zero_interest(self):self.assertAlmostEqual(_amortization(1000,0,10)[-1][1],0)
 def test_exit_value(self):
  f=project(self.p,self.r);self.assertAlmostEqual(f['sale_price'],f['year_11_noi']/.06)
 def test_growth_revenue(self):
  f=project(self.p,self.r,ForecastAssumptions(market_growth_pct=5,restricted_growth_pct=5))
  self.assertGreater(f['rows'][-1]['scheduled_rent'],f['rows'][0]['scheduled_rent'])
 def test_high_expense_weakens_noi(self):
  a=project(self.p,self.r,ForecastAssumptions(expense_inflation_pct=0))
  b=project(self.p,self.r,ForecastAssumptions(expense_inflation_pct=9))
  self.assertLess(b['rows'][-1]['noi'],a['rows'][-1]['noi'])
 def test_sale_reconciles(self):
  f=project(self.p,self.r)
  self.assertAlmostEqual(f['net_sale_to_equity'],f['sale_price']-f['selling_cost']-f['ending_debt'])
 def test_invalid_inputs(self):
  with self.assertRaises(ValueError):project(self.p,self.r,ForecastAssumptions(exit_cap_pct=0))
 def test_zero_equity_no_irr(self):
  p=replace(self.p,grant_m=100)
  f=project(p,analyze(p));self.assertIsNone(f['equity_irr'])
if __name__=='__main__':unittest.main()

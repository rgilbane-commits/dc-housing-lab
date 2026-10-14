import unittest
from dataclasses import replace
from model import Inputs, analyze
from cash_flow import annual_waterfall, waterfall_html
from display_format import money

class WaterfallTests(unittest.TestCase):
    def result(self,**kw):return annual_waterfall(analyze(replace(Inputs(),**kw)))
    def test_reconcile(self):
        w=self.result(); self.assertAlmostEqual(w['gross']-w['vacancy']-w['opex'],w['noi']);self.assertAlmostEqual(w['noi']-w['total_ds'],w['cash_to_equity'])
    def test_no_double_count_debt(self):
        w=self.result(); r=analyze(Inputs());self.assertAlmostEqual(w['noi'],r['noi'])
    def test_zero_debt(self):
        w=self.result(loan_m=0,private_debt_m=0);self.assertEqual(w['total_ds'],0);self.assertIsNone(w['total_dscr']);self.assertAlmostEqual(w['cash_to_equity'],w['noi'])
    def test_public_debt_reduces_cash(self):
        a=self.result(loan_m=0);b=self.result(loan_m=10);self.assertLess(b['cash_to_equity'],a['cash_to_equity']);self.assertAlmostEqual(a['noi'],b['noi'])
    def test_private_debt_reduces_cash(self):
        a=self.result(private_debt_m=0);b=self.result(private_debt_m=10);self.assertLess(b['cash_to_equity'],a['cash_to_equity'])
    def test_cash_on_cash_uses_required_equity(self):
        w=self.result(committed_equity_m=0);self.assertAlmostEqual(w['cash_on_cash_pct'],100*w['cash_to_equity']/w['equity_required']);self.assertGreater(w['equity_gap'],0)
    def test_commitment_does_not_change_return(self):
        a=self.result(committed_equity_m=0);b=self.result(committed_equity_m=50);self.assertEqual(a['cash_on_cash_pct'],b['cash_on_cash_pct'])
    def test_zero_equity_na(self):
        w=self.result(grant_m=200,private_debt_m=0,loan_m=0);self.assertIsNone(w['cash_on_cash_pct'])
    def test_negative_cash(self):
        w=self.result(loan_m=100,private_debt_m=0);self.assertLess(w['cash_to_equity'],0)
    def test_presentation_negative(self):
        w=self.result(loan_m=100,private_debt_m=0);html=waterfall_html(w,money);self.assertIn('Cash flow to equity',html);self.assertIn('-$',html)
    def test_revenue_only_cash(self):
        w=self.result(loan_m=0,private_debt_m=0,opex_pct=0,vacancy_pct=0);self.assertAlmostEqual(w['gross'],w['cash_to_equity'])
    def test_csv_amounts_are_numeric(self):
        w=self.result();self.assertTrue(all(isinstance(v,(int,float)) for _,v in w['rows']))
    def test_dscr(self):
        w=self.result();self.assertAlmostEqual(w['total_dscr'],w['noi']/w['total_ds'])
    def test_against_model_total_debt(self):
        r=analyze(Inputs());w=annual_waterfall(r);self.assertAlmostEqual(w['total_ds'],r['total_annual_debt_service'])
    def test_html_no_overflow(self):
        w=self.result(loan_m=500,private_debt_m=0);self.assertNotIn('width:1,',waterfall_html(w,money))

if __name__=='__main__':unittest.main()

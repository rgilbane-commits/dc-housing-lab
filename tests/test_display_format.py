import unittest
from display_format import money, money_millions, percentage, integer
from pathlib import Path
class DisplayFormattingQA(unittest.TestCase):
    def test_signed_compact_money(self):
        self.assertEqual(money(-3_250_000, compact=True), '-$3.25M')
        self.assertEqual(money(3_250_000, compact=True), '$3.25M')
    def test_small_values(self):
        self.assertEqual(money(-900), '-$900')
        self.assertEqual(money(0), '$0')
        self.assertEqual(money(12_345), '$12,345')
    def test_k_m_boundaries(self):
        self.assertEqual(money(1_000_000, compact=True), '$1.00M')
        self.assertEqual(money(95_000, compact=True), '$95.0K')
    def test_percentage_and_units(self):
        self.assertEqual(percentage(5.5), '5.5%')
        self.assertEqual(integer(1200), '1,200')
    def test_millions_unit(self):
        self.assertEqual(money_millions(-2.5), '-$2.50M')
    def test_tables_are_formatted_without_csv_mutation(self):
        app=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
        self.assertIn("'Amount ($)':lambda x: money(x)", app)
        self.assertIn('.to_csv(index=False)',app)
        self.assertNotIn("fm=lambda x:f'${abs(x)",app)
if __name__=='__main__':unittest.main()

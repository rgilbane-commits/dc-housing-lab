import unittest
from investment_strategy import Line, evaluate, AREAS, STRATEGIES, SUBSIDY_PER_HOME
class InvestmentTests(unittest.TestCase):
    def test_empty(self):
        r=evaluate([]);self.assertEqual(r['potential_capacity'],0);self.assertEqual(r['unallocated_m'],100)
    def test_budget(self):
        with self.assertRaises(ValueError):evaluate([Line(AREAS[0],STRATEGIES[0],101,250000)])
    def test_capacity_floor(self):
        r=evaluate([Line(AREAS[0],STRATEGIES[0],1.0,300000)])
        self.assertEqual(r['potential_capacity'],3);self.assertEqual(r['delivered_homes'],0)
    def test_zero_and_negative(self):
        self.assertEqual(evaluate([Line(AREAS[0],STRATEGIES[0],0,100000)])['potential_capacity'],0)
        for x in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):evaluate([Line(AREAS[0],STRATEGIES[0],x,100000)])
    def test_bad_support(self):
        for x in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):evaluate([Line(AREAS[0],STRATEGIES[0],2,x)])
    def test_gates(self):
        a=Line(AREAS[1],STRATEGIES[1],1,100000,True,True,False)
        b=Line(AREAS[0],STRATEGIES[0],1,200000,True,True,True)
        r=evaluate([a,b]);self.assertEqual(r['potential_capacity'],15);self.assertEqual(r['qualified_illustrative_capacity'],5);self.assertEqual(r['delivered_homes'],0)
    def test_duplicate(self):
        a=Line(AREAS[0],STRATEGIES[0],1,200000)
        with self.assertRaises(ValueError):evaluate([a,a])
    def test_unrecognized(self):
        with self.assertRaises(ValueError):evaluate([Line('Wrong',STRATEGIES[0],1,100000)])
    def test_budget_exact(self):
        r=evaluate([Line(AREAS[0],STRATEGIES[0],100,250000)])
        self.assertEqual(r['unallocated_m'],0);self.assertEqual(r['potential_capacity'],400)
if __name__=='__main__':unittest.main()

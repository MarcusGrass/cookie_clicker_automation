import unittest
from utils.optimal_calculations import *
from utils.dto import *


class TestOptimalCalculations(unittest.TestCase):

    def test_amount_to_cps(self):
        manual = 343*1800/0.15*7
        self.assertAlmostEqual(manual, get_min_amount_to_cps(343), 2)

    def test_best_value_option(self):
        products = [Product(9.491*10e18, 9.1*10e12, None), Product(2.43*10e18, 2.56*10e12, None)]
        self.assertEqual(2.43*10e18, get_best_value_product(products).cost)

        pairs = [(9.491 * 10e18, 9.1 * 10e12), (2.8 * 10e18, 2.56 * 10e12)]
        products = [Product(9.491 * 10e18, 9.1 * 10e12, None), Product(2.8 * 10e18, 2.56 * 10e12, None)]
        self.assertEqual(9.491 * 10e18, get_best_value_product(products).cost)

    def test_needed_min_amount(self):
        current_cps = 549*1e+12
        purchase_cost = 10.2*1e+18

        self.assertTrue(5e+19 < calculate_min_value_for_purchase(current_cps, purchase_cost) < 6e+19)

    def test_hourly_report(self):
        report = HourlyReport(5, 1, 15)
        report.calculate_hourly_report_stats(10, 3, 30)

        self.assertEqual(report.delta_balance, 5)
        self.assertEqual(report.delta_cps, 2)
        self.assertEqual(report.delta_hc, 15)

        self.assertEqual(100, report.balance_increase)
        self.assertEqual(200, report.cps_increase)
        self.assertEqual(100, report.hc_increase)


if __name__ == "__main__":
    unittest.main()

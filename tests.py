import unittest
from cookie_clicker_automation import CookieClickerAutomator


class ElementReadingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(ElementReadingTests, cls).setUpClass()
        cls.automator = CookieClickerAutomator()
        gamestate_file = "D:\\Program\\PycharmProjects\\seleniumtest\\save_files\\BagoolBakery (7).txt"
        cls.automator.load_game(custom_file=gamestate_file)

    @classmethod
    def tearDownClass(cls):
        del cls.automator

    def test_checking_values(self):
        self.automator.set_current_balance()
        cookie_amount = self.automator.current_balance

        self.assertTrue(67*1e+18 < cookie_amount.amount < 68*1e+18)
        print()
        print("CPS: ", cookie_amount.cps)
        print("CPS COMPENSATOR: ", self.automator.cps_compensator)
        self.assertTrue(310*1e+12 < cookie_amount.cps < 330*1e+12)

    def test_getting_product(self):
        elements = self.automator.get_all_product_elements()
        for element in elements:
            if 1*1e+19 < element.cost < 1.1*1e+19:
                self.assertTrue(9100000000000 < element.cps < 9300000000000)
            elif 2.6*1e+18 < element.cost < 2.8*1e+18:
                self.assertTrue(2400000000000 < element.cps < 2800000000000)
            elif 4.9*1e+16 < element.cost < 5.4*1e+16:
                self.assertTrue(150000000000.0 < element.cps < 160000000000.0)

    def test_getting_upgrades(self):
        pass


if __name__ == "__main__":
    unittest.main()

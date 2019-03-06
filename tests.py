import unittest
from cookie_clicker_automation import CookieClickerAutomator
from purchase_manager import PurchaseManager
from garden_manager import GardenManager


class ElementReadingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(ElementReadingTests, cls).setUpClass()
        cls.automator = CookieClickerAutomator()
        gamestate_file = "D:\\Program\\PycharmProjects\\seleniumtest\\save_files\\BagoolBakery (7).txt"
        cls.automator.load_game(custom_file=gamestate_file)
        cls.automator.close_popup_boxes()

    @classmethod
    def tearDownClass(cls):
        del cls.automator

    """
    def test_checking_values(self):
        self.automator.set_current_balance()
        cookie_amount = self.automator.current_balance

        self.assertTrue(67*1e+18 < cookie_amount.amount < 68*1e+18)
        self.assertTrue(310*1e+12 < cookie_amount.cps < 330*1e+12)

    def test_getting_upgrades(self):
        self.automator.set_current_balance()
        purchase_manager = PurchaseManager(self.automator.driver, self.automator.current_balance)
        purchase_manager.purchase_best_value_option()
    
    def test_reload(self):
        self.automator.load_game()
    """
    def test_managing_garden(self):
        self.automator.check_ascension_levels()
        print(self.automator.ascension_number)
        garden_manager = GardenManager(self.automator.driver)
        garden_manager.manage_garden()
        garden_manager = GardenManager(self.automator.driver)
        garden_manager.manage_garden()


if __name__ == "__main__":
    unittest.main()

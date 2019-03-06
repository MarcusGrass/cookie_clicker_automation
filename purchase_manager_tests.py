import unittest
from cookie_clicker_automation import CookieClickerAutomator
from purchase_manager import PurchaseManager


class ElementReadingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(ElementReadingTests, cls).setUpClass()
        cls.automator = CookieClickerAutomator()
        gamestate_file = "D:\\Program\\PycharmProjects\\seleniumtest\\vault\\file_with_unbought_buildings.txt"
        cls.automator.load_game(custom_file=gamestate_file)

    @classmethod
    def tearDownClass(cls):
        del cls.automator

    def test_getting_unowned(self):
        self.automator.set_current_balance()
        purchase_manager = PurchaseManager(self.automator.driver, self.automator.current_balance)
        purchase_manager.inspect_buildings()


if __name__ == "__main__":
    unittest.main()

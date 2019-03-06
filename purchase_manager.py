import time
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from utils.dto import *
from utils.parsing import *
from utils.optimal_calculations import *


class PurchaseManager(object):
    def __init__(self, driver, current_balance):
        self.driver = driver
        self.current_balance = current_balance
        self.buildings = list()
        self.upgrades = list()
        self.cheap_upgrade_elements = list()
        self.bought = str()

    def purchase_best_value_option(self):
        self.inspect_buildings()
        self.inspect_upgrades()
        self.set_value_of_upgrades()
        self.purchase_best_value_product()
        self.purchase_cheap_upgrades()
        time.sleep(1)
        return self.bought

    def inspect_buildings(self):
        building_elements = self.driver.find_elements_by_css_selector(".product.unlocked.enabled")
        building_list = list()
        max_tries = 10
        num_tries = 0
        for element in building_elements[-5:]:
            while num_tries < max_tries:
                try:
                    time.sleep(0.05)
                    action = ActionChains(self.driver)
                    action.move_to_element(self.driver.find_element_by_id("bigCookie"))
                    time.sleep(0.05)
                    action.move_to_element(element)
                    time.sleep(0.1)
                    action.perform()

                    raw_cost = self.driver.find_element_by_xpath(
                        "//div[@style='float:right;text-align:right;']"
                    ).text
                    num_cost = parse_product_cost(raw_cost)

                    raw_name = self.driver.find_element_by_xpath("//div[@class='name']").text
                    name = parse_product_name(raw_name)
                    if name == "wizard tower":
                        continue
                    try:
                        cps = self.driver.find_element_by_class_name("data").text
                        num_cps = parse_product_cps(cps)
                    except NoSuchElementException:
                        num_cps = None

                    building_list.append(Building(name, num_cost, num_cps, element))
                    num_tries = 0
                except Exception as e:
                    if isinstance(e, StaleElementReferenceException) or isinstance(e, NoSuchElementException):
                        time.sleep(0.1)
                        num_tries += 1
                        continue
                    else:
                        raise

                break

        self.buildings = building_list

    def inspect_upgrades(self):
        upgrade_elements = self.driver.find_elements_by_xpath(
            '//div[@id=\'upgrades\']/div[contains(@onclick,"Game.UpgradesById")]'
        )
        upgrade_list = list()
        max_tries = 10
        num_tries = 0
        for element in upgrade_elements:
            while num_tries < max_tries:
                try:
                    time.sleep(0.05)
                    action = ActionChains(self.driver)
                    action.move_to_element(self.driver.find_element_by_id("bigCookie"))
                    time.sleep(0.05)
                    upgrade_div = self.driver.find_element_by_xpath("//div[@id='upgrades']")
                    action.move_to_element(upgrade_div)
                    time.sleep(0.05)
                    action.move_to_element(element)
                    time.sleep(0.05)
                    action.perform()

                    raw_description = self.driver.find_element_by_xpath("//div[@class='description']").text

                    cost = self.driver.find_element_by_xpath("//div[@style='float:right;text-align:right;']/span").text
                    clean_cost = parse_product_cost(cost)
                    descriptor = parse_upgrade_description(raw_description)
                    if clean_cost < self.current_balance.cps * 30 and clean_cost < self.current_balance.amount / 25:
                        self.cheap_upgrade_elements.append(element)
                        logging.info("Found cheap upgrade element with text: %s\n"
                                     "its cost was %.2f and the current cps was %.2f" % (element.text, clean_cost,
                                                                                         self.current_balance.cps))
                        break
                    elif descriptor != "unknown upgrade":
                        upgrade_list.append(Upgrade(descriptor, clean_cost, element))

                except Exception as e:
                    if isinstance(e, StaleElementReferenceException) or isinstance(e, NoSuchElementException):
                        time.sleep(0.1)
                        num_tries += 1
                        continue
                break
        self.upgrades = upgrade_list

    def pre_process_unbought_buildings(self):
        for building in self.buildings:
            if building.cps is None:
                building.cps = self.current_balance.cps / 15

    def set_value_of_upgrades(self):
        for ind in range(len(self.upgrades)):
            if self.upgrades[ind].upgrade_type == "kitten":
                self.upgrades[ind].cps = self.current_balance.cps / 3
            elif type(self.upgrades[ind].upgrade_type) == float:
                self.upgrades[ind].cps = self.current_balance.cps * self.upgrades[ind].upgrade_type
            else:
                for product in self.buildings:
                    if product.name in self.upgrades[ind].upgrade_type:
                        try:
                            self.upgrades[ind].cps = product.cps * 2
                        except TypeError:
                            self.upgrades[ind].cps = 0

    def get_best_value_purchase(self):
        combined_list = self.buildings + self.upgrades
        ind = 0

        while ind < len(combined_list):
            if combined_list[ind].cost is None or combined_list[ind].cps is None:
                combined_list.pop(ind)
            else:
                ind += 1

        return get_best_value_product(combined_list)

    def purchase_best_value_product(self):
        self.pre_process_unbought_buildings()
        best_value = self.get_best_value_purchase()
        if self.current_balance.amount > calculate_min_value_for_purchase(
                self.current_balance.cps, best_value.cost):

            if type(best_value) == Upgrade:
                self.purchase_upgrade(best_value)
                self.bought = "Upgrade: %s." % best_value.upgrade_type
            elif type(best_value) == Building:
                self.purchase_building(best_value)
                self.bought = "Building: %s." % best_value.name
            else:
                raise Exception("Best value option is neither a building nor an upgrade.")
        else:
            if type(best_value) == Upgrade:
                logging.info("Purchase manager found best value to be upgrade %s.\n"
                             "With a cost of %.2f and a current max balance of %.2f and max cps %.2f "
                             "it was not worth the cost." % (best_value.upgrade_type, best_value.cost,
                                                             self.current_balance.amount, self.current_balance.cps))
            elif type(best_value) == Building:
                logging.info("Purchase manager found best value to be building %s.\n"
                             "With a cost of %.2f and a current max balance of %.2f and max cps %.2f "
                             "it was not worth the cost." % (best_value.name, best_value.cost,
                                                             self.current_balance.amount, self.current_balance.cps))
        time.sleep(0.3)

    def purchase_upgrade(self, upgrade):
        action = ActionChains(self.driver)
        action.move_to_element(self.driver.find_element_by_id("bigCookie"))
        time.sleep(0.05)
        upgrade_div = self.driver.find_element_by_xpath("//div[@id='upgrades']")
        action.move_to_element(upgrade_div)
        time.sleep(0.2)
        action.move_to_element(upgrade.element)
        time.sleep(0.2)
        action.perform()
        upgrade.element.click()

    def purchase_building(self, building):
        building.element.click()

    def purchase_cheap_upgrades(self):
        if len(self.cheap_upgrade_elements) > 0:
            element = self.cheap_upgrade_elements[0]
            num_tries = 0
            max_tries = 10
            while num_tries < max_tries:
                try:
                    time.sleep(0.05)
                    action = ActionChains(self.driver)
                    action.move_to_element(self.driver.find_element_by_id("bigCookie"))
                    time.sleep(0.05)
                    upgrade_div = self.driver.find_element_by_xpath("//div[@id='upgrades']")
                    action.move_to_element(upgrade_div)
                    time.sleep(0.05)
                    action.move_to_element(element)
                    time.sleep(0.05)
                    action.click(element)
                    time.sleep(0.05)
                    action.perform()

                except Exception as e:
                    if isinstance(e, StaleElementReferenceException) or isinstance(e, NoSuchElementException):
                        time.sleep(0.1)
                        num_tries += 1
                        continue
                break
            time.sleep(0.3)


if __name__ == "__main__":
    pass

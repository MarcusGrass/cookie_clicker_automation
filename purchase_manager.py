import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from utils.dto import *
from utils.parsing import *


class PurchaseManager(object):
    def __init__(self, driver):
        self.driver = driver

    def get_all_buildings(self):
        time.sleep(0.5)
        product_elements = self.driver.find_elements_by_css_selector(".product.unlocked.enabled")
        interesting_elements = product_elements[-5:]

        product_list = list()
        max_tries = 10
        num_tries = 0
        for element in interesting_elements:
            while num_tries < max_tries:
                try:
                    time.sleep(0.1)
                    action = ActionChains(self.driver)
                    action.move_to_element(self.driver.find_element_by_id("bigCookie"))
                    time.sleep(0.05)
                    action.move_to_element(element)
                    time.sleep(0.1)
                    action.perform()

                    raw_cost = self.driver.find_element_by_xpath("//div[@style='float:right;text-align:right;']").text
                    raw_cost_list = raw_cost.split(" ")
                    num_cost = translate_text_to_number(raw_cost_list[0], raw_cost_list[1])

                    raw_cps_string = repr(self.driver.find_element_by_class_name("data").text)
                    clean_cps_list = parse_product_cps(raw_cps_string).split(" ")
                    num_cps = translate_text_to_number(clean_cps_list[0], clean_cps_list[1])

                    print(raw_cost, raw_cps_string)
                    product_list.append(Product(num_cost, num_cps, element))
                except Exception as e:
                    if isinstance(e, StaleElementReferenceException) or isinstance(e, NoSuchElementException):
                        time.sleep(0.1)
                        num_tries += 1
                        continue
                break

        return product_list


if __name__ == "__main__":
    pass

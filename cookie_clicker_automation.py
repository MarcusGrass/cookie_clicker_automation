import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver, Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os
import time

from utils.filehandler import SaveFileHandler
from utils.optimal_calculations import *

URL = "http://orteil.dashnet.org/cookieclicker/"
CONSENT_COOKIE = {
    "name": "cookieconsent_dismissed",
    "value": "yes",
    'expiry': 1585095058.093486,
    "domain": ".dashnet.org"
}
PREFS = {
    "download.default_directory": "D:\\Program\\PycharmProjects\\seleniumtest\\save_files"
}
options = Options()
options.add_experimental_option("prefs", PREFS)


class CookieClickerAutomator(object):
    def __init__(self):
        self.gamestate_file = None
        self.driver = WebDriver(chrome_options=options)
        self.prefs_button = None

    def __del__(self):
        self.driver.close()
        print("Closed driver.")

    def run(self):
        self.load_game()
        try:
            while True:
                try:
                    self.check_for_shimmers()
                    time.sleep(2)
                    print("Found and clicked Golden Cookie!")
                    time.sleep(15)
                except NoSuchElementException:
                    pass
        except Exception:
            raise
        finally:
            self.save_game()

    def check_for_shimmers(self):
        shimmer = self.driver.find_element_by_class_name("shimmer")
        time.sleep(0.5)
        shimmer.click()
        time.sleep(0.5)

    def check_cookie_amount(self):
        raw_text = str(repr(self.driver.find_element_by_id("cookies").text)).replace("'", "")
        divided_text = raw_text.split("\\n")
        total_number, total_multipler = tuple(divided_text[0].split(" "))
        total_amount = translate_text_to_number(total_number, total_multipler)

        total_cps_number, total_cps_multiplier = tuple(divided_text[2].split(" ")[-2:])
        total_cps = translate_text_to_number(total_cps_number, total_cps_multiplier)
        return CookieAmount(total_amount, total_cps)

    def get_all_product_elements(self):
        time.sleep(0.5)
        product_elements = self.driver.find_elements_by_css_selector(".product.unlocked.enabled")
        interesting_elements = product_elements[-3:]

        product_list = list()

        for element in interesting_elements:

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

            product_list.append(Product(num_cost, num_cps, element))

        return product_list

    def purchase_best_value_product(self):
        products = self.get_all_product_elements()
        time.sleep(1)
        best_value = get_best_value_product(products)

        current_balance = self.check_cookie_amount()
        if current_balance.amount > calculate_min_value_for_purchase(current_balance.cps, best_value.cost):
            best_value.element.click()
        time.sleep(2)

    def get_gamestate_file(self):
        file_handler = SaveFileHandler()
        self.gamestate_file = file_handler.get_latest_save_file_name()
        print("Loaded gamestate file: %s" % self.gamestate_file)

    def load_game(self):
        self.get_gamestate_file()

        self.driver.get(URL)

        time.sleep(1)

        self.driver.add_cookie(CONSENT_COOKIE)
        self.driver.get(URL)

        self.set_prefs_button()
        self.prefs_button.click()
        time.sleep(0.5)

        load_element = self.driver.find_element_by_id("FileLoadInput")
        load_element.send_keys(self.gamestate_file)
        time.sleep(1)
        self.prefs_button.click()
        time.sleep(0.5)

    def set_prefs_button(self):
        self.prefs_button = self.driver.find_element_by_id("prefsButton")

    def save_game(self):
        self.prefs_button.click()
        time.sleep(0.5)
        save_button = self.driver.find_element_by_xpath(
            '//a[contains(@onclick,"Game.FileSave();PlaySound(\'snd/tick.mp3\');")]'
        )
        save_button.click()
        time.sleep(2)


class CookieAmount(object):
    def __init__(self, amount, cps):
        self.amount = amount
        self.cps = cps


def translate_text_to_number(number, text):
    number = float(number)
    multiplier = translate_word_to_multiplier(text)
    return number*multiplier


def translate_word_to_multiplier(text):
    multiplier = 1
    if text == "million":
        multiplier = 1e+6
    elif text == "billion":
        multiplier = 1e+9
    elif text == "trillion":
        multiplier = 1e+12
    elif text == "quadrillion":
        multiplier = 1e+15
    elif text == "quintillion":
        multiplier = 1e+18
    elif text == "sextillion":
        multiplier = 1e+21
    elif text == "septillion":
        multiplier = 1e+24
    elif text == "octillion":
        multiplier = 1e+27
    elif text == "nonillion":
        multiplier = 1e+30

    return multiplier


def parse_product_cps(hover_string):
    interesting_string = hover_string.split("\\n")[0]
    start_ind = interesting_string.find("produces") + len("produces")
    end_ind = interesting_string.find("cookies")
    return interesting_string[start_ind+1: end_ind-1]


if __name__ == "__main__":
    # "E:\\Downloads\\BagoolBakery.txt"
    cka = CookieClickerAutomator()
    cka.load_game()
    while True:
        time.sleep(0.2)
        cka.purchase_best_value_product()


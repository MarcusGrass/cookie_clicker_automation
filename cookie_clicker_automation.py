from selenium.webdriver.chrome.webdriver import WebDriver, Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException

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
        self.cps_compensator = 1
        self.next_is_clot = False
        self.mana = 0

    def __del__(self):
        self.driver.close()
        print("Closed driver.")

    def run(self):
        self.load_game()
        try:
            while True:
                time.sleep(1)
                self.purchase_best_value_product()
                self.click_shimmers_if_exists()
                self.cast_spell_if_buffed()
        except Exception:
            raise
        finally:
            self.save_game()

    def click_shimmers_if_exists(self):
        try:
            shimmer = self.driver.find_element_by_class_name("shimmer")
            time.sleep(0.5)
            shimmer.click()
            time.sleep(0.5)
        except NoSuchElementException:
            pass

    def check_cookie_amount(self):
        raw_text = str(repr(self.driver.find_element_by_id("cookies").text)).replace("'", "")
        divided_text = raw_text.split("\\n")
        total_number, total_multipler = tuple(divided_text[0].split(" "))
        total_amount = translate_text_to_number(total_number, total_multipler)

        total_cps_number, total_cps_multiplier = tuple(divided_text[2].split(" ")[-2:])
        total_cps = translate_text_to_number(total_cps_number, total_cps_multiplier)
        return CookieAmount(total_amount, total_cps)

    def cast_conjure_goods(self):
        self.close_popup_boxes()
        toggle_button = self.driver.find_element_by_id("productMinigameButton7")

        action = ActionChains(self.driver)
        action.move_to_element(toggle_button)
        action.perform()
        time.sleep(2)

        if "Close" in toggle_button.text:
            toggle_button.click()
        time.sleep(0.1)

        action = ActionChains(self.driver)
        action.move_to_element(toggle_button)
        action.perform()
        time.sleep(2)

        toggle_button.click()
        time.sleep(0.5)
        spell_cast_button = self.driver.find_element_by_id("grimoireSpell0")
        spell_cast_button.click()
        self.close_popup_boxes()
        time.sleep(0.2)
        toggle_button.click()
        time.sleep(0.5)

    def cast_spell_if_buffed(self):
        buffs = self.check_buffs()
        time.sleep(0.2)
        frenzy_in_buffs = False
        for buff in buffs:
            if "frenzy" in buff:
                frenzy_in_buffs = True
            if "clot" in buff:
                frenzy_in_buffs = False
                break
        if frenzy_in_buffs:
            mana = self.check_mana()
            time.sleep(0.2)
            if mana >= 4:
                self.save_game()

                self.cast_conjure_goods()

                buffs = self.check_buffs()
                if "clot" in buffs:
                    self.load_game()
                    self.next_is_clot = True

        elif self.next_is_clot:
            mana = self.check_mana()
            time.sleep(0.2)
            if mana >= 4:
                self.cast_conjure_goods()
        time.sleep(0.2)

    def check_buffs(self):
        buffs = self.driver.find_elements_by_class_name("pieTimer")
        active_buffs = list()
        for element in buffs:
            try:
                self.move_to_neutral_element()
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.perform()
                time.sleep(0.2)
                buff_info = self.driver.find_element_by_xpath(
                    "//div[@style='min-width:200px;text-align:center;font-size:11px;margin:8px 0px;']"
                )
                active_buffs.append(parse_buff_text(buff_info.text))
            except StaleElementReferenceException:
                pass

        self.set_buff_multiplier(active_buffs)
        return active_buffs

    def set_buff_multiplier(self, buffs):
        if "frenzy" in buffs and "clot" not in buffs:
            self.cps_compensator = 1/6
        elif "frenzy" in buffs and "clot" in buffs:
            self.cps_compensator = 1/3
        elif "clot" in buffs:
            self.cps_compensator = 2
        else:
            self.cps_compensator = 1

    def check_mana(self):
        self.close_popup_boxes()
        toggle_button = self.driver.find_element_by_id("productMinigameButton7")

        action = ActionChains(self.driver)
        action.move_to_element(toggle_button)
        action.perform()
        time.sleep(0.2)

        if "Close" in toggle_button.text:
            toggle_button.click()

        time.sleep(0.2)
        toggle_button.click()
        time.sleep(0.2)
        mana_text = self.driver.find_element_by_id("grimoireBarText").text
        time.sleep(0.2)
        self.close_popup_boxes()
        toggle_button.click()
        self.move_to_neutral_element()
        time.sleep(0.2)
        self.mana = parse_mana_string(mana_text)
        return parse_mana_string(mana_text)

    def close_popup_boxes(self):
        while True:
            try:
                self.driver.find_element_by_class_name("close").click()
            except Exception as e:
                if isinstance(e, StaleElementReferenceException) or isinstance(e, ElementNotVisibleException):
                    break
            time.sleep(0.1)

    def get_all_product_elements(self):
        time.sleep(0.5)
        product_elements = self.driver.find_elements_by_css_selector(".product.unlocked.enabled")
        interesting_elements = product_elements[-3:]

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

                    product_list.append(Product(num_cost, num_cps, element))
                except StaleElementReferenceException:
                    print("Failed to find element, try number: %s" % num_tries)
                    time.sleep(0.1)
                    num_tries += 1
                break

        return product_list

    def purchase_best_value_product(self):
        products = self.get_all_product_elements()
        time.sleep(1)
        best_value = get_best_value_product(products)

        current_balance = self.check_cookie_amount()
        if current_balance.amount > calculate_min_value_for_purchase(current_balance.cps, best_value.cost):
            best_value.element.click()
        time.sleep(2)

    def move_to_neutral_element(self):
        action = ActionChains(self.driver)
        action.move_to_element(self.driver.find_element_by_id("bigCookie"))
        action.perform()
        time.sleep(0.2)

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


def parse_mana_string(mana_string):
    return int(mana_string[0])


def parse_buff_text(buff_text):
    if "Frenzy" in buff_text and "x7" in buff_text:
        return "frenzy"
    elif "click frenzy" in buff_text.lower():
        return "click frenzy"
    elif "clot" in buff_text.lower():
        return "clot"
    else:
        return None


if __name__ == "__main__":
    cka = CookieClickerAutomator()
    cka.run()
from selenium.webdriver.chrome.webdriver import WebDriver, Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, WebDriverException

import time
import datetime
from utils.filehandler import SaveFileHandler
from utils.optimal_calculations import *
from utils.parsing import *
from utils.dto import *
from purchase_manager import PurchaseManager

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
        self.golden_cookie_clicks = 0
        self.last_save_time = datetime.datetime.now()
        self.current_balance = None

    def __del__(self):
        self.driver.close()
        print("Closed driver.")

    def run(self):
        self.load_game()
        try:
            num_tries = 0
            max_tries = 10
            while max_tries > num_tries:
                try:
                    time.sleep(1)
                    self.close_popup_boxes()
                    self.purchase_best_value_product()
                    self.click_shimmers_if_exists()
                    self.cast_spell_if_buffed()
                    if (datetime.datetime.now() - self.last_save_time).seconds > 300:
                        time.sleep(0.2)
                        self.save_game()
                        time.sleep(0.2)
                        file_handler = SaveFileHandler()
                        file_handler.clean_up_directory()
                    num_tries = 0
                except WebDriverException as e:
                    time.sleep(1)
                    num_tries += 1
                    self.close_popup_boxes()
                    print("Severe exception: %s was raised" % e)
                    time.sleep(1)
                    if num_tries % 4 == 0:
                        print("After four failed attempts reload is initialized.")
                        self.save_game()
                        time.sleep(1)
                        self.load_game()
                    continue

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
            self.golden_cookie_clicks += 1
            print("Clicked %s golden cookies so far." % self.golden_cookie_clicks)
        except NoSuchElementException:
            pass

    def set_current_balance(self):
        raw_text = str(repr(self.driver.find_element_by_id("cookies").text)).replace("'", "")
        divided_text = raw_text.split("\\n")
        total_number, total_multipler = tuple(divided_text[0].split(" "))
        total_amount = translate_text_to_number(total_number, total_multipler)

        total_cps_number, total_cps_multiplier = tuple(divided_text[2].split(" ")[-2:])
        total_cps = translate_text_to_number(total_cps_number, total_cps_multiplier)

        buffs = self.check_buffs()
        self.set_buff_multiplier(buffs)

        compensated_cps = total_cps * self.cps_compensator
        self.current_balance = CookieAmount(total_amount, compensated_cps)

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
        if frenzy_in_buffs and self.next_is_clot is False:
            mana = self.check_mana()
            time.sleep(0.2)
            if mana >= 6:
                self.save_game()

                self.cast_conjure_goods()

                buffs = self.check_buffs()
                if "clot" in buffs:
                    self.load_game()
                    self.next_is_clot = True

        elif frenzy_in_buffs is False and self.next_is_clot:
            mana = self.check_mana()
            time.sleep(0.2)
            if mana >= 6:
                self.cast_conjure_goods()
                self.next_is_clot = False
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
            except Exception as e:
                if isinstance(e, NoSuchElementException) or isinstance(e, StaleElementReferenceException):
                    pass

        self.set_buff_multiplier(active_buffs)
        return active_buffs

    def set_buff_multiplier(self, buffs):
        if len(buffs) == 1 and "frenzy" in buffs and "clot" not in buffs:
            self.cps_compensator = 1/6
        elif len(buffs) == 2 and "frenzy" in buffs and "clot" in buffs:
            self.cps_compensator = 1/3
        else:
            self.cps_compensator = 50

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
        closable = self.driver.find_elements_by_class_name("close")
        for element in closable:
            time.sleep(0.1)
            try:
                time.sleep(0.1)
                element.click()
            except Exception as e:
                if isinstance(e, StaleElementReferenceException) or isinstance(e, ElementNotVisibleException):
                    break
        time.sleep(0.1)

    def get_all_product_elements(self):
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

    def get_upgrade_elements(self):
        pass

    def purchase_best_value_product(self):
        products = self.get_all_product_elements()
        time.sleep(1)
        best_value = get_best_value_product(products)
        self.set_current_balance()
        if self.current_balance.amount > calculate_min_value_for_purchase(
                self.current_balance.cps, best_value.cost):
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

    def load_game(self, custom_file=False):
        if custom_file:
            self.gamestate_file = custom_file
            print("Loaded custom file: %s" % custom_file)
        else:
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
        self.prefs_button.click()
        self.last_save_time = datetime.datetime.now()
        time.sleep(2)


if __name__ == "__main__":
    cka = CookieClickerAutomator()
    cka.run()

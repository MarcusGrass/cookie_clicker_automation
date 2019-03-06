from selenium.webdriver.chrome.webdriver import WebDriver, Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, WebDriverException

import time
import datetime
import re

from utils.filehandler import SaveFileHandler
from utils.parsing import *
from utils.dto import *
from purchase_manager import PurchaseManager
from garden_manager import GardenManager
from time_coordinator import TimeCoordinator
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
        self.ascension_number = 0
        self.buffs = list()
        self.bought_this_run = list()

        self.time_coordinator = TimeCoordinator()

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
                    time.sleep(0.6)
                    self.click_shimmers_if_exists()
                    self.close_popup_boxes()
                    self.click_shimmers_if_exists()
                    self.purchase_best_value_product()
                    self.click_shimmers_if_exists()
                    self.cast_spell_if_buffed()
                    self.click_shimmers_if_exists()
                    if self.time_coordinator.time_to_save():
                        time.sleep(0.1)
                        self.save_game()
                        self.time_coordinator.last_save_time = datetime.datetime.now()
                        time.sleep(0.2)
                        file_handler = SaveFileHandler()
                        file_handler.clean_up_directory()
                    elif self.time_coordinator.time_to_plant_seeds():
                        self.close_popup_boxes()
                        garden_manager = GardenManager(self.driver)
                        garden_manager.manage_garden()
                        del garden_manager
                        self.time_coordinator.last_garden_plant_time = datetime.datetime.now()

                    elif self.time_coordinator.time_to_log_economy():
                        self.check_ascension_levels()
                        print()
                        print("%s:" % datetime.datetime.now())
                        print("Golden cookies/reindeer clicked this run: %s" % self.golden_cookie_clicks)
                        print("Current bank: %s" % self.current_balance.amount)
                        print("Current compensated cps: %s (with active buffs: %s)" %
                              (self.current_balance.cps, self.buffs))
                        print("Current heavenly chips: %s" % self.ascension_number)
                        print("Bought %s this pass." % self.bought_this_run)
                        print()
                        self.bought_this_run = list()
                        self.time_coordinator.last_economy_report = datetime.datetime.now()
                    num_tries = 0
                except WebDriverException as e:
                    time.sleep(1)
                    num_tries += 1
                    self.close_popup_boxes()
                    print("Severe exception: %s was raised" % e)
                    time.sleep(1)
                    if num_tries % 4 == 0:
                        print("After four failed attempts reload is initialized.")
                        try:
                            self.save_game()
                        except Exception as e:
                            print("Failed to save,reloading anyway, exception: %s" % e)
                        time.sleep(1)
                        self.load_game()
                    continue

        except Exception:
            raise
        finally:
            self.save_game()

    def click_shimmers_if_exists(self):
        try:
            shimmers = self.driver.find_elements_by_class_name("shimmer")
            for element in shimmers:
                time.sleep(0.05)
                element.click()
                time.sleep(0.2)
                self.golden_cookie_clicks += 1
        except NoSuchElementException:
            pass

    def set_current_balance(self):
        raw_text = str(repr(self.driver.find_element_by_id("cookies").text)).replace("'", "")
        divided_text = raw_text.split("\\n")
        total_number, total_multipler = tuple(divided_text[0].split(" "))
        try:
            total_amount = translate_text_to_number(total_number, total_multipler)
        except ValueError:
            total_amount = float(total_multipler.replace(" ", "").replace(":", "").replace(",", ""))

        total_cps_number, total_cps_multiplier = tuple(divided_text[2].split(" ")[-2:])
        try:
            total_cps = translate_text_to_number(total_cps_number, total_cps_multiplier)
        except ValueError:
            total_cps = float(total_cps_multiplier.replace(" ", "").replace(":", "").replace(",", ""))

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
                self.close_popup_boxes()
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
        self.buffs = active_buffs
        return active_buffs

    def set_buff_multiplier(self, buffs):
        if len(buffs) == 0:
            self.cps_compensator = 1
        elif len(buffs) == 1 and "frenzy" in buffs and "clot" not in buffs:
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

    def purchase_best_value_product(self):
        time.sleep(0.5)
        self.set_current_balance()
        purchase_manager = PurchaseManager(self.driver, self.current_balance)
        bought_item = purchase_manager.purchase_best_value_option()
        if bought_item != "":
            self.bought_this_run.append(bought_item)
        del purchase_manager
        self.move_to_neutral_element()
        time.sleep(0.2)

    def move_to_neutral_element(self):
        action = ActionChains(self.driver)
        action.move_to_element(self.driver.find_element_by_id("bigCookie"))
        action.perform()
        time.sleep(0.2)

    def get_gamestate_file(self):
        file_handler = SaveFileHandler()
        self.gamestate_file = file_handler.get_latest_save_file_name()
        print("Loaded gamestate file: %s" % self.gamestate_file)

    def check_ascension_levels(self):
        ascension_text = self.driver.find_element_by_xpath("//div[@id='ascendNumber']").text
        self.ascension_number = re.sub("[^0-9]", "", ascension_text)

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
        time.sleep(1)


if __name__ == "__main__":
    cka = CookieClickerAutomator()
    cka.run()

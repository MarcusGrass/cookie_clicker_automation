import time
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import logging


class GardenManager(object):
    """
    Cycle time 4*3600 seconds.
    """
    def __init__(self, driver):
        self.driver = driver
        self.available_plots = list()

    def manage_garden(self):
        logging.info("Doing a garden check at time: %s" % datetime.now())
        self.toggle_garden("view")
        self.make_sure_right_soil_selected()
        self.get_all_empty_available_garden_plots()
        self.plant_seeds()
        time.sleep(0.2)
        self.toggle_garden("close")
        time.sleep(0.2)

    def toggle_garden(self, state):

        toggle_button = self.driver.find_element_by_xpath("//div[@id='productMinigameButton2']")

        action = ActionChains(self.driver)
        action.move_to_element(toggle_button)
        action.perform()
        time.sleep(0.2)

        if "Close" in toggle_button.text.lower():
            toggle_button.click()
        time.sleep(0.2)

        toggle_button = self.driver.find_element_by_xpath("//div[@id='productMinigameButton2']")
        actions = ActionChains(self.driver)
        actions.move_to_element(toggle_button)
        actions.perform()
        time.sleep(0.2)

        if state in toggle_button.text.lower():
            toggle_button.click()
            time.sleep(0.2)

    def get_all_empty_available_garden_plots(self):
        available_plots = self.driver.find_elements_by_xpath(
            "//div[contains(@class,'gardenTile') and "
            "contains(@style,'display: block;')]"
        )
        logging.info("Garden manager found %s garden tiles." % len(available_plots))
        for element in available_plots:
            try:
                element.find_element_by_xpath("./div[contains(@style, 'display:none;')]")
                self.available_plots.append(element)
            except NoSuchElementException:
                pass
        logging.info("Garden manager found %s available plots for planting new seeds." % len(self.available_plots))

    def plant_seeds(self):
        seed_element = self.driver.find_element_by_xpath("//div[@id='gardenSeed-0']")
        for empty_plot in self.available_plots:
            actions = ActionChains(self.driver)
            actions.move_to_element(seed_element)
            actions.perform()
            time.sleep(0.2)
            actions = ActionChains(self.driver)
            actions.click(seed_element)
            actions.perform()
            time.sleep(0.2)
            actions = ActionChains(self.driver)
            actions.move_to_element(empty_plot)
            actions.perform()
            time.sleep(0.2)
            actions = ActionChains(self.driver)
            actions.click(empty_plot)
            actions.perform()
            time.sleep(0.2)

    def make_sure_right_soil_selected(self):
        soil_element = self.driver.find_element_by_xpath("//div[@id='gardenSoil-2']")
        actions = ActionChains(self.driver)
        actions.move_to_element(soil_element)
        actions.click(soil_element)
        actions.perform()
        time.sleep(0.2)


if __name__ == "__main__":
    pass

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.config_reader import ConfigReader


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, ConfigReader.get_explicit_wait())

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator):
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def send_keys(self, locator, text):
        """Clear the field and type `text`.

        Uses Ctrl+A + Delete (instead of `.clear()`) and dispatches a manual
        `input` event, since React-controlled inputs can silently ignore
        `.clear()` and end up appending instead of replacing the value.
        """
        element = self.find_element(locator)
        element.click()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            element,
        )
        element.send_keys(text)

    def is_displayed(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()

    def is_element_visible(self, locator, timeout=None):
        """Wait up to `timeout` (default = explicit wait) for visibility.

        Returns False instead of raising if the element never becomes visible.
        """
        wait_time = timeout or ConfigReader.get_explicit_wait()
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_any_visible(self, *locators):
        """Wait until any of the given locators becomes visible; return the matched element."""
        conditions = [EC.visibility_of_element_located(loc) for loc in locators]
        return self.wait.until(EC.any_of(*conditions))

    def get_text(self, locator):
        return self.find_element(locator).text

    def click(self, locator):
        def click_fresh_element(driver):
            try:
                element = driver.find_element(*locator)
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    return True
            except (
                ElementClickInterceptedException,
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                return False
            return False

        self.wait.until(click_fresh_element)

    def wait_to_be_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click_dropdown_option(self, locator, expected_text=None):
        def click_available_option(driver):
            try:
                options = driver.find_elements(*locator)
                expected = self._normalize_text(expected_text)

                for option in options:
                    option_text = self._normalize_text(option.text)
                    if not option_text or (expected and expected not in option_text):
                        continue

                    if option.is_displayed() and option.is_enabled():
                        option.click()
                        return True
            except (
                ElementClickInterceptedException,
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                return False
            return False

        self.wait.until(click_available_option)

    @staticmethod
    def _normalize_text(value):
        return " ".join((value or "").split()).casefold()
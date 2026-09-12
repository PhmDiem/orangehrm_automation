import logging

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config_reader import ConfigReader

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            self.driver, ConfigReader.get_explicit_wait()
        )
        self._last_submit_completed = False

    # --- Element interactions ---

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator):
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def send_keys(self, locator, text):
        element = self.find_element(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        element.click()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            element,
        )
        element.send_keys(text)

    def is_displayed(self, locator):
        return self.wait.until(
            EC.visibility_of_element_located(locator)
        ).is_displayed()

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
        conditions = [
            EC.visibility_of_element_located(loc) for loc in locators
        ]
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
                    if not option_text or (
                        expected and expected not in option_text
                    ):
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

    def get_text_when_ready(self, locator, timeout=None):
        """Wait until the element's text is non-empty, then return it.

        Unlike get_text(), this handles SPA cases where the element exists
        in the DOM before its content has finished rendering.
        """
        wait_time = timeout or ConfigReader.get_explicit_wait()
        element = WebDriverWait(self.driver, wait_time).until(
            lambda d: (
                d.find_element(*locator)
                if d.find_element(*locator).text.strip()
                else False
            )
        )
        return element.text

    def wait_for_loading_to_disappear(self, timeout=None):
        wait_time = timeout or ConfigReader.get_explicit_wait()
        loader_locator = (
            By.CSS_SELECTOR,
            ".oxd-loading-spinner, .oxd-form-loader, .oxd-table-loader",
        )

        def loaders_are_gone(driver):
            try:
                return all(
                    not loader.is_displayed()
                    for loader in driver.find_elements(*loader_locator)
                )
            except StaleElementReferenceException:
                # OrangeHRM replaces loader nodes as the SPA re-renders.
                # Re-query them on the next poll instead of failing the action.
                return False

        try:
            WebDriverWait(self.driver, wait_time).until(
                loaders_are_gone
            )
        except TimeoutException:
            logger.error(
                "Spinner did not disappear after %ss. Current URL: %s",
                wait_time,
                self.driver.current_url,
            )
            raise

    def wait_for_table_result(self, row_locator, empty_locator, timeout=None):
        """Wait until a table has rows or displays its empty-state message."""
        self.wait_for_loading_to_disappear()
        wait_time = timeout or ConfigReader.get_timeout("feedback")

        return WebDriverWait(self.driver, wait_time).until(
            lambda driver: bool(driver.find_elements(*row_locator))
            or any(
                element.is_displayed()
                for element in driver.find_elements(*empty_locator)
            )
        )

    def wait_for_empty_table(self, row_locator, empty_locator, timeout=None):
        """Wait until a table displays its empty state and has no rows."""
        self.wait_for_loading_to_disappear()
        wait_time = timeout or ConfigReader.get_timeout("feedback")

        return WebDriverWait(self.driver, wait_time).until(
            lambda driver: any(
                element.is_displayed()
                for element in driver.find_elements(*empty_locator)
            )
            and not driver.find_elements(*row_locator)
        )

    def confirm_delete_dialog(self, locator):
        """Confirm a delete dialog and wait until its request finishes."""
        self.click(locator)
        self.wait_for_loading_to_disappear()

    def click_via_js(self, locator):
        """Click an element via JS, bypassing Selenium's visibility check.

        Useful for custom-styled radio/checkbox inputs whose native <input>
        is visually hidden behind a styled label/span.
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def submit_and_wait(self, locator):
        """Submit a form and wait for its loading state to finish."""
        self._last_submit_completed = False
        self.click(locator)
        self.wait_for_loading_to_disappear()
        self._last_submit_completed = True

    def was_last_submit_completed(self, success_locator=None, success_text=None):
        """Wait for and confirm the expected successful-submit feedback."""
        if not success_locator:
            return False

        expected_text = self._normalize_text(success_text)
        try:
            return WebDriverWait(
                self.driver, ConfigReader.get_timeout("feedback")
            ).until(
                lambda driver: any(
                    element.is_displayed()
                    and (
                        not expected_text
                        or expected_text in self._normalize_text(element.text)
                    )
                    for element in driver.find_elements(*success_locator)
                )
            )
        except TimeoutException:
            return False

    @staticmethod
    def _normalize_text(value):
        return " ".join((value or "").split()).casefold()

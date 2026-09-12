from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Locators ---
        self.login_title = (
            By.XPATH,
            '//h5[@class="oxd-text oxd-text--h5 orangehrm-login-title"]',
        )
        self.username_field = (By.NAME, "username")
        self.password_field = (By.NAME, "password")
        self.click_btn = (By.XPATH, '//button[@type="submit"]')
        self.Invalid_error_message = (
            By.XPATH,
            '//p[@class="oxd-text oxd-text--p oxd-alert-content-text"]',
        )
        self.required_error_message = (
            By.XPATH,
            '//span[@class="oxd-text oxd-text--span '
            'oxd-input-field-error-message oxd-input-group__message"]',
        )
        self.user_dropdown = (
            By.XPATH,
            '//span[@class="oxd-userdropdown-tab"]',
        )
        self.logout_btn = (By.XPATH, '//a[contains(@href, "/auth/logout")]')

    # --- Actions ---

    def login(self, username, password):
        self.send_keys(self.username_field, username)
        self.send_keys(self.password_field, password)
        self.click(self.click_btn)

    def login_and_wait(self, username, password, dashboard_locator):
        self.login(username, password)
        if self.is_element_visible(
            self.Invalid_error_message,
            timeout=ConfigReader.get_timeout("medium"),
        ):
            raise AssertionError(
                f"Login failed for '{username}': {self.get_error_message()}"
            )
        self.wait.until(lambda d: d.find_element(*dashboard_locator).is_displayed())

    # --- Verification ---

    def is_login_displayed(self):
        return self.is_displayed(self.login_title)

    def get_error_message(self):
        element = self.wait_for_any_visible(
            self.Invalid_error_message,
            self.required_error_message,
        )
        return element.text

    def logout(self):
        self.click(self.user_dropdown)
        self.click(self.logout_btn)

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class ContactDetailsPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        """Page object for the logged-in user's My Info > Contact Details tab."""

        self.contact_details_heading = (By.XPATH, "//h6[normalize-space()='Contact Details']")
        self.contact_details_tab = (
            By.XPATH,
            "//a[contains(@class,'orangehrm-tabs-item') and normalize-space()='Contact Details']",
        )

        # Address
        self.street_1 = (By.XPATH, "//label[normalize-space()='Street 1']/following::input[1]")
        self.street_2 = (By.XPATH, "//label[normalize-space()='Street 2']/following::input[1]")
        self.city = (By.XPATH, "//label[normalize-space()='City']/following::input[1]")
        self.state_province = (By.XPATH, "//label[normalize-space()='State/Province']/following::input[1]")
        self.zip_postal_code = (By.XPATH, "//label[normalize-space()='Zip/Postal Code']/following::input[1]")
        self.country = (
            By.XPATH,
            "//label[normalize-space()='Country']/following::div[contains(@class,'oxd-select-text')][1]",
        )

        # Telephone
        self.home_telephone = (By.XPATH, "//label[normalize-space()='Home']/following::input[1]")
        self.mobile = (By.XPATH, "//label[normalize-space()='Mobile']/following::input[1]")
        self.work_telephone = (By.XPATH, "//label[normalize-space()='Work']/following::input[1]")

        # Email
        self.other_email = (By.XPATH, "//label[normalize-space()='Other Email']/following::input[1]")

        # Actions & feedback
        self.save_button = (
            By.XPATH,
            "//h6[normalize-space()='Contact Details']/following::button[@type='submit'][1]",
        )
        self.success_toast = (By.CSS_SELECTOR, ".oxd-toast--success")
        self.success_message = (
            By.CSS_SELECTOR,
            ".oxd-toast-content--success .oxd-toast-message",
        )
        self.form_loader = (By.CSS_SELECTOR, ".oxd-form-loader")
        self.required_error = (By.XPATH, "//span[normalize-space()='Required']")
        self.field_error_message = (
            By.XPATH,
            "//span[contains(@class,'oxd-input-field-error-message')]",
        )
        self.mobile_error_message = (
            By.XPATH,
            "//label[normalize-space()='Mobile']/following::span[contains(@class,'oxd-input-field-error-message')][1]",
        )

    def open_contact_details(self):
        self.click(self.contact_details_tab)
        return self.is_displayed(self.contact_details_heading)

    def enter_street_1(self, value):
        self.send_keys(self.street_1, value)

    def enter_city(self, value):
        self.send_keys(self.city, value)

    def enter_mobile(self, value):
        self.send_keys(self.mobile, value)

    def get_field_value(self, locator):
        return self.driver.find_element(*locator).get_attribute("value") or ""

    def get_mobile_value(self):
        return self.driver.find_element(*self.mobile).get_attribute("value")

    def save(self):
        self.submit_and_wait(self.save_button)

    def is_saved(self):
        return self.was_last_submit_completed(
            self.success_message,
            "successfully updated",
        )

    def has_field_error(self):
        return self.is_element_visible(self.field_error_message, timeout=ConfigReader.get_timeout("medium"))

    def get_mobile_error_text(self):
        return self.wait.until(
            lambda driver: (
                element.text.strip()
                if (element := driver.find_element(*self.mobile_error_message)).is_displayed()
                and element.text.strip()
                else False
            )
        )

    def get_field_error_texts(self):
        return [el.text for el in self.find_elements(self.field_error_message) if el.text.strip()]
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class EmergencyContactsPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        """Page object for the logged-in user's My Info > Emergency Contacts tab."""

        self.emergency_contacts_tab = (
            By.XPATH,
            "//a[contains(@class,'orangehrm-tabs-item') and normalize-space()='Emergency Contacts']",
        )
        self.list_heading = (By.XPATH, "//h6[normalize-space()='Assigned Emergency Contacts']")
        self.add_button = (By.XPATH, "//button[contains(normalize-space(.), 'Add')]")

        # Add/Save form
        self.form_heading = (By.XPATH, "//h6[normalize-space()='Save Emergency Contact']")
        self.name = (By.XPATH, "//label[normalize-space()='Name']/following::input[1]")
        self.relationship = (By.XPATH, "//label[normalize-space()='Relationship']/following::input[1]")
        self.home_telephone = (By.XPATH, "//label[normalize-space()='Home Telephone']/following::input[1]")
        self.mobile = (By.XPATH, "//label[normalize-space()='Mobile']/following::input[1]")
        self.work_telephone = (By.XPATH, "//label[normalize-space()='Work Telephone']/following::input[1]")

        self.cancel_button = (By.XPATH, "//button[@type='button' and normalize-space()='Cancel']")
        self.save_button = (By.XPATH, "//button[@type='submit']")

        self.success_toast = (By.CSS_SELECTOR, ".oxd-toast--success")
        self.required_error = (By.XPATH, "//span[normalize-space()='Required']")
        self.emergency_rows = (By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")

    def open_emergency_contacts(self):
        self.click(self.emergency_contacts_tab)
        return self.is_displayed(self.list_heading)

    def add_emergency_contact(self):
        self.click(self.add_button)
        return self.is_displayed(self.form_heading)

    def enter_emergency_contact(self, name, relationship, mobile=""):
        self.send_keys(self.name, name)
        self.send_keys(self.relationship, relationship)
        if mobile:
            self.send_keys(self.mobile, mobile)

    def save(self):
        self.click(self.save_button)

    def is_saved(self):
        return self.is_element_visible(self.success_toast, timeout=ConfigReader.get_timeout("feedback"))

    def has_required_error(self):
        return self.is_element_visible(self.required_error, timeout=ConfigReader.get_timeout("medium"))

    def get_emergency_rows_text(self):
        return [row.text for row in self.find_elements(self.emergency_rows)]

    def wait_for_emergency_contact(self, name):
        return self.wait.until(
            lambda driver: any(
                name in row.text
                for row in driver.find_elements(*self.emergency_rows)
            )
        )
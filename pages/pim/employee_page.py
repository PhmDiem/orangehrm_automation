from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class EmployeePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.personal_details_heading = (
            By.XPATH,
            '//h6[text()="Personal Details"]',
        )
        self.employee_full_name = (
            By.XPATH,
            '//div[contains(@class,"orangehrm-edit-employee-name")]/h6',
        )
        self.employee_list_btn = (By.XPATH, '//a[text()="Employee List"]')
        self.gender_male_radio = (
            By.XPATH,
            '//input[@type="radio"][@value="1"]',
        )
        self.gender_female_radio = (
            By.XPATH,
            '//input[@type="radio"][@value="2"]',
        )
        self.dob_input = (
            By.XPATH,
            '//label[text()="Date of Birth"]/following::input[1]',
        )
        self.blood_type_dropdown = (
            By.XPATH,
            '//label[text()="Blood Type"]/following::div[contains(@class,"oxd-select-text")][1]',
        )
        self.blood_type_option = (By.XPATH, '//div[@role="listbox"]//span')
        self.save_btn = (By.XPATH, '//button[@type="submit"]')
        self.success_toast = (
            By.XPATH,
            '//div[contains(@class,"oxd-toast--success")]',
        )

    def navigate_to_employee_list(self):
        self.click(self.employee_list_btn)

    def is_personal_details_displayed(self):
        return super().is_displayed(self.personal_details_heading)

    def get_displayed_full_name(self):
        return self.get_text_when_ready(self.employee_full_name)

    def is_personal_details_displayed_immediate(self):
        return self.is_element_visible(
            self.personal_details_heading, timeout=3
        )

    def select_gender(self, gender):
        self.wait_for_loading_to_disappear()
        locator = (
            self.gender_male_radio
            if gender.lower() == "male"
            else self.gender_female_radio
        )
        self.click_via_js(locator)

    def enter_dob(self, dob):
        self.send_keys(self.dob_input, dob)
        element = self.find_element(self.dob_input)
        element.send_keys(Keys.TAB)

    def select_blood_type(self, blood_type):
        self.click(self.blood_type_dropdown)
        self.click_dropdown_option(
            self.blood_type_option, expected_text=blood_type
        )

    def is_blood_type_available(self):
        return self.is_element_visible(self.blood_type_dropdown, timeout=2)

    def click_save(self):
        self.click(self.save_btn)

    def is_update_success_displayed(self):
        return self.is_element_visible(self.success_toast, timeout=5)

    def get_dob_value(self):
        return self.find_element(self.dob_input).get_attribute("value")

    def wait_for_dob_value(self, expected_value, timeout=None):
        """Wait until the SPA has rendered the saved date back into the field."""
        wait_time = timeout or ConfigReader.get_explicit_wait()
        return WebDriverWait(self.driver, wait_time).until(
            lambda driver: (
                value
                if (value := driver.find_element(*self.dob_input).get_attribute("value"))
                == expected_value
                else False
            )
        )

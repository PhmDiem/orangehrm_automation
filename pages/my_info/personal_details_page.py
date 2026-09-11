from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class PersonalDetailsPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        """Page object for the logged-in user's My Info > Personal Details tab."""

        # Heading & tab navigation
        self.personal_details_heading = (By.XPATH, "//h6[normalize-space()='Personal Details']")
        self.personal_details_tab = (
            By.XPATH,
            "//a[contains(@class,'orangehrm-tabs-item') and normalize-space()='Personal Details']",
        )

        # Employee Full Name
        self.first_name = (By.XPATH, "//input[@name='firstName']")
        self.middle_name = (By.XPATH, "//input[@name='middleName']")
        self.last_name = (By.XPATH, "//input[@name='lastName']")

        # Identity fields
        self.employee_id = (By.XPATH, "//label[normalize-space()='Employee Id']/following::input[1]")
        self.other_id = (By.XPATH, "//label[normalize-space()='Other Id']/following::input[1]")
        self.driver_license_number = (
            By.XPATH,
            "//label[normalize-space()=\"Driver's License Number\"]/following::input[1]",
        )
        self.license_expiry_date = (
            By.XPATH,
            "//label[normalize-space()='License Expiry Date']/following::input[1]",
        )

        # Nickname / Blood Type - optional fields, not always configured
        self.nickname = (By.XPATH, "//label[normalize-space()='Nickname']/following::input[1]")
        self.blood_type = (
            By.XPATH,
            "//label[normalize-space()='Blood Type']/following::div[contains(@class,'oxd-select-text')][1]",
        )
        self.blood_type_options = (By.XPATH, "//div[@role='listbox']//span")

        # Nationality / Marital Status / DOB / Gender
        self.nationality = (
            By.XPATH,
            "//label[normalize-space()='Nationality']/following::div[contains(@class,'oxd-select-text')][1]",
        )
        self.marital_status = (
            By.XPATH,
            "//label[normalize-space()='Marital Status']/following::div[contains(@class,'oxd-select-text')][1]",
        )
        self.date_of_birth = (By.XPATH, "//label[normalize-space()='Date of Birth']/following::input[1]")
        self.gender_male = (By.XPATH, "//input[@type='radio' and @value='1']")
        self.gender_female = (By.XPATH, "//input[@type='radio' and @value='2']")
        self.gender_male_label = (
            By.XPATH,
            "//label[.//input[@type='radio' and @value='1']]",
        )

        # Actions & feedback
        self.save_button = (
            By.XPATH,
            "//h6[normalize-space()='Personal Details']/following::button[@type='submit'][1]",
        )
        self.success_toast = (By.CSS_SELECTOR, ".oxd-toast--success")
        self.success_message = (
            By.CSS_SELECTOR,
            ".oxd-toast-content--success .oxd-toast-message",
        )
        self.form_loader = (By.CSS_SELECTOR, ".oxd-form-loader")
        self.required_error = (By.XPATH, "//span[normalize-space()='Required']")

    def open(self):
        return self.is_displayed(self.personal_details_heading)

    def open_personal_details(self):
        self.click(self.personal_details_tab)
        return self.is_displayed(self.personal_details_heading)

    def enter_nickname_if_available(self, nickname):
        """Nickname field is optional / may not be configured on the demo site."""
        if not self.is_element_visible(self.nickname, timeout=ConfigReader.get_timeout("short")):
            return False
        self.send_keys(self.nickname, nickname)
        return True

    def get_nickname_value(self):
        return self.driver.find_element(*self.nickname).get_attribute("value")

    def get_blood_type_value(self):
        return self.driver.find_element(*self.blood_type).text.strip()

    def select_gender(self, gender):
        locator = self.gender_male if gender.casefold() == "male" else self.gender_female
        self.click_via_js(locator)

    def is_gender_selected(self, gender):
        locator = self.gender_male if gender.casefold() == "male" else self.gender_female
        return self.driver.find_element(*locator).is_selected()

    def is_gender_control_visible(self):
        return self.is_element_visible(self.gender_male_label)

    def select_blood_type_if_available(self, blood_type):
        if not self.is_element_visible(self.blood_type, timeout=ConfigReader.get_timeout("short")):
            return False
        self.click(self.blood_type)
        self.click_dropdown_option(self.blood_type_options, expected_text=blood_type)
        return True

    def save(self):
        self.submit_and_wait(self.save_button)

    def is_saved(self):
        return self.was_last_submit_completed(
            self.success_message,
            "successfully updated",
        )
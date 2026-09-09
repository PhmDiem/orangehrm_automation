from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MyInfoPage(BasePage):
    """Page object for the logged-in user's My Info module."""

    personal_details_heading = (By.XPATH, "//h6[normalize-space()='Personal Details']")
    contact_details_heading = (By.XPATH, "//h6[normalize-space()='Contact Details']")
    emergency_contacts_heading = (
        By.XPATH,
        "//h6[normalize-space()='Emergency Contacts']",
    )
    personal_details_tab = (By.XPATH, "//a[normalize-space()='Personal Details']")
    contact_details_tab = (By.XPATH, "//a[normalize-space()='Contact Details']")
    emergency_contacts_tab = (
        By.XPATH,
        "//a[normalize-space()='Emergency Contacts']",
    )
    save_buttons = (By.XPATH, "//button[@type='submit']")
    success_toast = (By.CSS_SELECTOR, ".oxd-toast--success")
    required_error = (By.XPATH, "//span[normalize-space()='Required']")

    nickname = (By.XPATH, "//label[normalize-space()='Nickname']/following::input[1]")
    gender_male = (By.XPATH, "//input[@type='radio' and @value='1']")
    gender_female = (By.XPATH, "//input[@type='radio' and @value='2']")
    blood_type = (
        By.XPATH,
        "//label[normalize-space()='Blood Type']/following::div[contains(@class,'oxd-select-text')][1]",
    )
    blood_type_options = (By.XPATH, "//div[@role='listbox']//span")

    emergency_add_button = (By.XPATH, "//button[contains(normalize-space(.), 'Add')]")
    emergency_name = (
        By.XPATH,
        "//label[normalize-space()='Name']/following::input[1]",
    )
    emergency_relationship = (
        By.XPATH,
        "//label[normalize-space()='Relationship']/following::input[1]",
    )
    emergency_mobile = (
        By.XPATH,
        "//label[normalize-space()='Mobile']/following::input[1]",
    )
    emergency_rows = (By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")

    def open(self):
        return self.is_displayed(self.personal_details_heading)

    def open_personal_details(self):
        self.click(self.personal_details_tab)
        return self.is_displayed(self.personal_details_heading)

    def open_contact_details(self):
        self.click(self.contact_details_tab)
        return self.is_displayed(self.contact_details_heading)

    def open_emergency_contacts(self):
        self.click(self.emergency_contacts_tab)
        return self.is_displayed(self.emergency_contacts_heading)

    def enter_nickname(self, nickname):
        self.send_keys(self.nickname, nickname)

    def select_gender(self, gender):
        locator = self.gender_male if gender.casefold() == "male" else self.gender_female
        self.click_via_js(locator)

    def select_blood_type_if_available(self, blood_type):
        if not self.is_element_visible(self.blood_type, timeout=2):
            return False
        self.click(self.blood_type)
        self.click_dropdown_option(self.blood_type_options, expected_text=blood_type)
        return True

    def save(self):
        self.click(self.save_buttons)

    def is_saved(self):
        return self.is_element_visible(self.success_toast, timeout=5)

    def add_emergency_contact(self):
        self.click(self.emergency_add_button)

    def enter_emergency_contact(self, name, relationship, mobile):
        self.send_keys(self.emergency_name, name)
        self.send_keys(self.emergency_relationship, relationship)
        self.send_keys(self.emergency_mobile, mobile)

    def get_emergency_rows_text(self):
        return [row.text for row in self.find_elements(self.emergency_rows)]

    def has_required_error(self):
        return self.is_element_visible(self.required_error, timeout=3)

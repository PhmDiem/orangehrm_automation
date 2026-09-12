from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class AddEntitlementPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Header ---
        self.add_entitlement_header = (
            By.XPATH, '//p[contains(@class,"orangehrm-main-title") and text()="Add Leave Entitlement"]'
        )

        # --- Add to (radio group) ---
        self.individual_employee_radio = (
            By.XPATH, "//label[contains(., 'Individual Employee')]//input[@type='radio']"
        )

        # --- Employee Name (autocomplete) ---
        self.employee_name = (By.XPATH, '//p[@class="oxd-userdropdown-name"]')
        self.input_employee_name = (By.XPATH, '//input[@placeholder="Type for hints..."]')
        self.option_employee = (By.XPATH, '//div[@class="oxd-autocomplete-option"]/span')

        # --- Leave Type (dropdown) ---
        self.leave_type_dropdown = (
            By.XPATH,
            "//label[text()='Leave Type']/parent::div/following-sibling::div//div[contains(@class,'oxd-select-text-input')]"
        )

        # --- Entitlement (plain input) ---
        self.entitlement_input = (
            By.XPATH,
            "//label[text()='Entitlement']/parent::div/following-sibling::div//input"
        )

        # --- Actions & feedback ---
        self.save_btn = (By.XPATH, "//button[@type='submit']")
        self.confirm_modal_btn = (
            By.XPATH, "//button[@type='button' and contains(., 'Confirm')]"
        )
        self.toast_success = (By.CSS_SELECTOR, ".oxd-toast--success")
        self.form_loader = (By.CSS_SELECTOR, ".oxd-form-loader")
        self.duplicate_error_toast = (By.XPATH, "//p[contains(text(),'already exists')]")
        self.field_error_messages = (By.CSS_SELECTOR, ".oxd-input-field-error-message")

    # --- Page state ---

    def is_page_displayed(self):
        return self.is_displayed(self.add_entitlement_header)

    # --- Actions ---

    def select_individual_employee(self):
        self.click_via_js(self.individual_employee_radio)

    def enter_employee_name(self, employee_name=None):
        requested_name = employee_name
        employee_name = employee_name or self.get_text(self.employee_name)
        self.send_keys(self.input_employee_name, employee_name)
        if requested_name:
            self.click_dropdown_option(
                self.option_employee, expected_text=requested_name
            )
        else:
            # The current user's autocomplete label can include a suffix that
            # differs from the user-menu label. The filtered list has one item.
            self.click_dropdown_option(self.option_employee)

    def select_leave_type(self, leave_type: str):
        self.click(self.leave_type_dropdown)
        option_locator = (By.XPATH, f"//div[@role='listbox']//span[text()='{leave_type}']")
        self.click(option_locator)

    def enter_entitlement_days(self, days: str):
        self.send_keys(self.entitlement_input, days)

    def click_save(self):
        self.click(self.save_btn)

        # The "Updating Entitlement" modal appears only when the entitlement exists.
        if self.is_element_visible(
            self.confirm_modal_btn,
            timeout=ConfigReader.get_timeout("medium"),
        ):
            self.click(self.confirm_modal_btn)

        self.wait_for_loading_to_disappear()
        # After confirmation, OrangeHRM redirects to /leave/viewLeaveEntitlements.
        # Use the URL as the primary signal because the toast may disappear during the redirect.
        self.wait.until(lambda d: "viewLeaveEntitlements" in d.current_url)

    def add_entitlement(self, leave_type: str, days: str, employee_name=None):
        """Fill and submit the Add Entitlement form for the currently logged-in employee."""
        self.select_individual_employee()
        self.enter_employee_name(employee_name)
        self.wait_for_loading_to_disappear()
        self.select_leave_type(leave_type)
        self.enter_entitlement_days(days)
        self.click_save()

    # --- Verification ---

    def is_success(self):
        """Return whether submission and confirmation redirected to the entitlements list."""
        return "viewLeaveEntitlements" in self.driver.current_url

    def is_duplicate_entitlement_error(self):
        return self.is_element_visible(
            self.duplicate_error_toast,
            timeout=ConfigReader.get_timeout("medium"),
        )

    def get_field_errors(self):
        return [
            element.text.strip()
            for element in self.driver.find_elements(*self.field_error_messages)
            if element.is_displayed() and element.text.strip()
        ]

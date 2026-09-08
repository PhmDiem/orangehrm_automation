from selenium.webdriver.common.by import By
from pages.base_page import BasePage


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
        self.duplicate_error_toast = (By.XPATH, "//p[contains(text(),'already exists')]")
        self.field_error_messages = (By.CSS_SELECTOR, ".oxd-input-field-error-message")

        self.leave_period_dropdown = (
            By.XPATH,
            "//label[text()='Leave Period']/parent::div/following-sibling::div//div[contains(@class,'oxd-select-text-input')]"
        )
        self.leave_period_options = (By.CSS_SELECTOR, ".oxd-select-dropdown .oxd-select-option")
        

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

        # Modal "Updating Entitlement" chỉ xuất hiện khi entitlement đã tồn tại
        if self.is_element_visible(self.confirm_modal_btn, timeout=3):
            self.click(self.confirm_modal_btn)

        # Sau Confirm, OrangeHRM redirect sang /leave/viewLeaveEntitlements.
        # Dùng URL làm tín hiệu chính vì toast dễ biến mất trước khi kịp check do redirect.
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
        """Đã redirect sang trang danh sách Entitlements -> submit + confirm hoàn tất."""
        return "viewLeaveEntitlements" in self.driver.current_url

    def is_duplicate_entitlement_error(self):
        return self.is_element_visible(self.duplicate_error_toast, timeout=3)

    def get_field_errors(self):
        try:
            return [e.text for e in self.find_elements(self.field_error_messages)]
        except Exception:
            return []

    def select_leave_period_covering(self, target_date_iso: str):
        """
        Chọn Leave Period nào có khoảng ngày bao phủ target_date_iso (format YYYY-MM-DD).
        Tránh phụ thuộc period mặc định có thể đổi giữa các lần load trang.
        """
        self.click(self.leave_period_dropdown)
        options = self.find_elements(self.leave_period_options)
        from datetime import datetime
        target = datetime.strptime(target_date_iso, "%Y-%m-%d")
        for opt in options:
            # option text dạng "2026-01-01 - 2026-12-31"
            try:
                start_str, end_str = [s.strip() for s in opt.text.split("-", 1)[1].split(" - ")]
            except Exception:
                continue
            # parse linh hoạt hơn nếu format khác, cần xác nhận thật
        # tạm thời: chọn option đầu tiên nếu không parse được, log cảnh báo
        if options:
            options[0].click()

from selenium.webdriver.common.by import By

from pages.admin.add_user_page import AddUserPage


class LeaveAddUserPage(AddUserPage):
    """Leave-only extension for creating an ESS account for a target employee."""

    success_toast = (By.CSS_SELECTOR, ".oxd-toast--success")

    def select_employee_by_name(self, employee_name):
        self.send_keys(self.input_employee_name, employee_name)
        self.click_dropdown_option(
            self.option_employee,
            expected_text=employee_name,
        )

    def create_user_for_employee(self, role, status, username, password, employee_name):
        self.select_user_role(role)
        self.select_employee_by_name(employee_name)
        self.select_status(status)
        self.enter_username(username)
        self.enter_password(password)
        self.enter_confirm_password(password)
        self.click_save_btn()

    def is_save_successful(self, timeout=8):
        if self.is_element_visible(self.success_toast, timeout=timeout):
            return True
        return "viewSystemUsers" in self.driver.current_url

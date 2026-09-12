from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from pages.admin.add_user_page import AddUserPage


class LeaveAddUserPage(AddUserPage):
    """Leave-only extension for creating an ESS account for a target employee."""

    # --- Feedback locators ---

    success_toast = (By.CSS_SELECTOR, ".oxd-toast--success")

    # --- Employee selection ---

    def select_employee_by_name(self, employee_name):
        """Select a newly-created employee after its Admin search index updates."""
        expected = self._normalize_text(employee_name)

        for attempt in range(3):
            self.send_keys(self.input_employee_name, employee_name)
            try:
                def select_matching_option(driver):
                    for option in driver.find_elements(*self.option_employee):
                        if (
                            option.is_displayed()
                            and expected in self._normalize_text(option.text)
                        ):
                            option.click()
                            return True
                    return False

                WebDriverWait(self.driver, 10).until(select_matching_option)
                return
            except TimeoutException:
                if attempt == 2:
                    raise

    # --- User creation ---

    def create_user_for_employee(self, role, status, username, password, employee_name):
        self.select_user_role(role)
        self.select_employee_by_name(employee_name)
        self.select_status(status)
        self.enter_username(username)
        self.enter_password(password)
        self.enter_confirm_password(password)
        self.click_save_btn()

    # --- Verification ---

    def is_save_successful(self, timeout=8):
        """Confirm save only after the Add User route has finished changing.

        The success toast is rendered before OrangeHRM completes its redirect
        to System Users. Treating that toast as completion allowed the next
        navigation to interrupt the SPA transition and yield a blank page.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: "viewSystemUsers" in driver.current_url
            )
            return True
        except TimeoutException:
            return False

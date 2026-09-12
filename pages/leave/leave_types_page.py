from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LeaveTypesPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Locators ---
        self.leave_types = (By.XPATH, '//h6[text()="Leave Types"]')
        self.leave_type_list = (By.CSS_SELECTOR, ".oxd-table")
        self.leave_type_rows = (By.CSS_SELECTOR, ".oxd-table .oxd-table-card")

    # --- Verification ---

    def is_leave_types_page_displayed(self):
        return super().is_displayed(self.leave_types)

    def is_leave_types_list_displayed(self):
        return super().is_displayed(self.leave_type_list)

    def get_leave_type_row_count(self):
        return len(self.find_elements(self.leave_type_rows))

    
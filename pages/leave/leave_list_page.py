from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LeaveListPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.leave = (By.XPATH, '//h6[text()="Leave"]')

        self.entitlements_menu = (
            By.XPATH, '//span[normalize-space(.)="Entitlements"]'
        )
        self.add_entitlement_link = (By.XPATH, '//a[text()="Add Entitlements"]')
        self.employee_entitlements_link = (
            By.XPATH, '//a[text()="Employee Entitlements"]'
        )
        self.my_entitlements_link = (By.XPATH, '//a[text()="My Entitlements"]')

        self.configure_btn = (By.XPATH, '//span[normalize-space(.)="Configure"]')
        self.leave_types_btn = (By.XPATH, '//a[text()="Leave Types"]')

        self.apply_menu_item = (By.XPATH, '//a[text()="Apply"]')
        self.my_leave_menu_item = (By.XPATH, '//a[text()="My Leave"]')
        self.leave_list_menu_item = (By.XPATH, '//a[text()="Leave List"]')

        # OrangeHRM renders this page title as h5 (unlike most module pages).
        self.leave_list_header = (By.XPATH, '//h5[normalize-space()="Leave List"]')
        self.table_rows = (
            By.XPATH, "//div[@class='oxd-table-body']//div[@role='row']"
        )
        self.employee_name_input = (
            By.XPATH, '//label[normalize-space()="Employee Name"]/following::input[1]'
        )
        self.status_dropdown = (
            By.XPATH,
            '//label[contains(normalize-space(),"Show Leave with Status")]'
            '/following::div[contains(@class,"oxd-select-text")][1]',
        )
        self.status_options = (By.CSS_SELECTOR, '.oxd-select-dropdown .oxd-select-option')
        self.selected_status_close = (
            By.CSS_SELECTOR,
            '.oxd-chip-close',
        )
        self.search_btn = (By.XPATH, '//button[@type="submit"]')

        self.approve_btn_relative = (
            By.XPATH,
            ".//button[normalize-space()='Approve' or .//*[normalize-space()='Approve']]",
        )
        self.reject_btn_relative = (
            By.XPATH,
            ".//button[normalize-space()='Reject' or .//*[normalize-space()='Reject']]",
        )

    def is_leave_page_displayed(self):
        return self.is_displayed(self.leave)

    def navigate_to_leave_types(self):
        self.click(self.configure_btn)
        self.click(self.leave_types_btn)

    def navigate_to_add_entitlement(self):
        self.click(self.entitlements_menu)
        self.click(self.add_entitlement_link)

    def navigate_to_employee_entitlements(self):
        self.click(self.entitlements_menu)
        self.click(self.employee_entitlements_link)

    def navigate_to_my_entitlements(self):
        self.click(self.entitlements_menu)
        self.click(self.my_entitlements_link)

    def navigate_to_apply_leave(self):
        self.click(self.apply_menu_item)

    def navigate_to_my_leave(self):
        self.click(self.my_leave_menu_item)

    def navigate_to_leave_list(self):
        self.click(self.leave_list_menu_item)

    def is_page_displayed(self):
        return self.is_displayed(self.leave_list_header)

    def search_pending_leave_for_employee(self, employee_name: str):
        while True:
            close_buttons = self.driver.find_elements(*self.selected_status_close)
            if not close_buttons:
                break
            close_buttons[0].click()
            self.wait_for_loading_to_disappear()

        self.send_keys(self.employee_name_input, employee_name)
        self.click_dropdown_option(
            (By.CSS_SELECTOR, '.oxd-autocomplete-option'),
            expected_text=employee_name,
        )
        self.click(self.status_dropdown)
        self.click_dropdown_option(
            self.status_options, expected_text='Pending Approval'
        )
        self.click(self.search_btn)
        self.wait_for_loading_to_disappear()

    def find_row_by_marker(self, marker: str):
        """
        Find the row containing the unique marker from the Comments field.
        Do not assume the first row is the target because multiple pending
        requests from previous runs may coexist in the list.
        Return the row WebElement, or None when no matching row is found.
        """
        rows = self.find_elements(self.table_rows)
        for row in rows:
            if marker in row.text:
                return row
        return None

    def approve_leave_by_marker(self, marker: str):
        row = self.find_row_by_marker(marker)
        assert row is not None, f"Could not find leave request with marker '{marker}' in Leave List"
        row.find_element(*self.approve_btn_relative).click()
        self.wait_for_loading_to_disappear()

    def reject_leave_by_marker(self, marker: str):
        row = self.find_row_by_marker(marker)
        assert row is not None, f"Could not find leave request with marker '{marker}' in Leave List"
        row.find_element(*self.reject_btn_relative).click()
        self.wait_for_loading_to_disappear()

    def get_status_by_marker(self, marker: str) -> str:
        row = self.find_row_by_marker(marker)
        assert row is not None, f"Could not find leave request with marker '{marker}' in Leave List"
        return row.text

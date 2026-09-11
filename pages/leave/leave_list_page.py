from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LeaveListPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

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
        Tìm đúng dòng chứa marker duy nhất (từ ô Comments) trong Leave List,
        tránh giả định 'dòng đầu tiên là dòng cần thao tác' - vì có thể có
        nhiều leave request Pending khác (leftover từ các lần chạy trước)
        cùng tồn tại trong danh sách.
        Trả về WebElement của dòng đó, hoặc None nếu không tìm thấy.
        """
        rows = self.find_elements(self.table_rows)
        for row in rows:
            if marker in row.text:
                return row
        return None

    def approve_leave_by_marker(self, marker: str):
        row = self.find_row_by_marker(marker)
        assert row is not None, f"Không tìm thấy leave request với marker '{marker}' trong Leave List"
        row.find_element(*self.approve_btn_relative).click()
        self.wait_for_loading_to_disappear()

    def reject_leave_by_marker(self, marker: str):
        row = self.find_row_by_marker(marker)
        assert row is not None, f"Không tìm thấy leave request với marker '{marker}' trong Leave List"
        row.find_element(*self.reject_btn_relative).click()
        self.wait_for_loading_to_disappear()

    def get_status_by_marker(self, marker: str) -> str:
        row = self.find_row_by_marker(marker)
        assert row is not None, f"Không tìm thấy leave request với marker '{marker}' trong Leave List"
        return row.text

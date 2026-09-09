from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class MyLeavePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.my_leave_header = (By.XPATH, '//h6[text()="My Leave"]')
        self.leave_list_table = (By.CSS_SELECTOR, ".oxd-table")
        self.table_rows = (
            By.XPATH, "//div[@class='oxd-table-body']//div[@role='row']"
        )

    def is_page_displayed(self):
        return self.is_displayed(self.my_leave_header)

    def is_leave_list_visible(self):
        return self.is_element_visible(self.leave_list_table, timeout=5)

    def get_status_for_leave(self, from_date_ui: str, to_date_ui: str) -> str:
        """
        Tìm đúng dòng chứa khoảng ngày (theo format UI hiển thị, vd '2026-12-09')
        vừa apply, trả về text status của dòng đó.
        Trả về None nếu không tìm thấy dòng nào khớp.
        """
        rows = self.find_elements(self.table_rows)
        for row in rows:
            row_text = row.text
            if from_date_ui in row_text and to_date_ui in row_text:
                return row_text
        return None

    def is_leave_pending(self, from_date_ui: str, to_date_ui: str) -> bool:
        row_text = self.get_status_for_leave(from_date_ui, to_date_ui)
        if row_text is None:
            return False
        return "pending" in row_text.lower()

    def get_row_by_marker(self, marker: str):
        """Tìm dòng chứa đúng marker duy nhất (từ ô Comments), đảm bảo
        xác định chính xác request vừa tạo, không nhầm với bất kỳ request nào khác
        dù có thể trùng ngày tháng/leave type với request cũ."""
        rows = self.find_elements(self.table_rows)
        for row in rows:
            if marker in row.text:
                return row.text
        return None

    def cancel_leave_by_marker(self, marker: str):
        """Cancel a pending request created by the current test."""
        row_locator = (
            By.XPATH,
            f"//div[@class='oxd-table-body']//div[@role='row'][contains(., '{marker}')]",
        )
        row = self.find_element(row_locator)
        cancel_button = row.find_element(
            By.XPATH, ".//button[contains(normalize-space(.), 'Cancel')]"
        )
        cancel_button.click()

        confirm_button = (By.XPATH, "//button[contains(normalize-space(.), 'Yes, Confirm')]")
        if self.is_element_visible(confirm_button, timeout=3):
            self.click(confirm_button)

        # OrangeHRM keeps the row and changes its status to Cancelled.
        self.wait.until(
            lambda driver: any(
                "cancel" in row.text.lower()
                for row in driver.find_elements(*row_locator)
            )
        )

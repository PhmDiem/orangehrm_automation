from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


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
        Find the row containing the applied date range in the UI format
        (for example, '2026-12-09') and return its status text.
        Return None when no matching row is found.
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
        """Find the row containing the unique Comments marker.

        This identifies the newly created request even when an older request
        has the same dates or leave type.
        """
        def find_matching_row(driver):
            for row in driver.find_elements(*self.table_rows):
                if marker in row.text:
                    return row.text
            return False

        try:
            return WebDriverWait(
                self.driver, ConfigReader.get_timeout("feedback")
            ).until(find_matching_row)
        except TimeoutException:
            return None

    def wait_for_status_by_marker(self, marker: str, expected_status: str):
        expected_status = expected_status.casefold()

        def find_status(driver):
            for row in driver.find_elements(*self.table_rows):
                row_text = row.text
                if marker in row_text and expected_status in row_text.casefold():
                    return row_text
            return False

        return WebDriverWait(
            self.driver, ConfigReader.get_timeout("feedback")
        ).until(find_status)

    def cancel_leave_by_marker(self, marker: str) -> bool:
        """Cancel a request by marker when its current status allows cancellation.

        Approved/scheduled and pending requests expose a row-level ``Cancel``
        action. Rejected or already-cancelled requests do not; that is an
        expected state during teardown rather than an automation failure.
        """
        row_locator = (
            By.XPATH,
            f"//div[@class='oxd-table-body']//div[@role='row'][contains(., '{marker}')]",
        )
        cancel_button = (
            By.XPATH,
            f"{row_locator[1]}//button[normalize-space()='Cancel']",
        )
        if not self.driver.find_elements(*cancel_button):
            return False

        self.click(cancel_button)

        confirm_button = (By.XPATH, "//button[contains(normalize-space(.), 'Yes, Confirm')]")
        if self.is_element_visible(
            confirm_button,
            timeout=ConfigReader.get_timeout("medium"),
        ):
            self.click(confirm_button)

        # OrangeHRM keeps the row and changes its status to Cancelled.
        self.wait.until(
            lambda driver: any(
                "cancel" in row.text.lower()
                for row in driver.find_elements(*row_locator)
            )
        )
        return True

# pages/leave/leave_entitlements_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LeaveEntitlementsPage(BasePage):
    """Trang /leave/viewLeaveEntitlements - danh sách entitlements.

    Có 2 cách vào trang này:
    1. Tự động redirect sau khi Add Entitlement thành công
       (kèm query params empNumber, leaveTypeId, startDate, endDate).
    2. Vào thủ công qua menu Entitlements (không kèm params, hiển thị đầy đủ).
    """

    def __init__(self, driver):
        super().__init__(driver)

        self.entitlement_table = (By.CSS_SELECTOR, ".oxd-table")
        self.entitlement_rows = (By.CSS_SELECTOR, ".oxd-table .oxd-table-card")

    def is_on_this_page(self) -> bool:
        return "viewLeaveEntitlements" in self.driver.current_url

    def is_table_displayed(self):
        return self.is_element_visible(self.entitlement_table, timeout=5)

    def get_row_count(self):
        return len(self.find_elements(self.entitlement_rows))
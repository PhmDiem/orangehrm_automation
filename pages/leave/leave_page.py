from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains


class LeavePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.leave = (By.XPATH, '//h6[text()="Leave"]')

        # --- Entitlements dropdown (top-level topbar item) ---
        self.entitlements_menu = (
            By.XPATH, '//span[normalize-space(.)="Entitlements"]'
        )
        self.add_entitlement_link = (By.XPATH, '//a[text()="Add Entitlements"]')

        # --- Configure dropdown ---
        self.configure_btn = (By.XPATH, '//span[normalize-space(.)="Configure"]')
        self.leave_types_btn = (By.XPATH, '//a[text()="Leave Types"]')

        # --- Direct topbar tabs ---
        self.apply_menu_item = (By.XPATH, '//a[text()="Apply"]')
        self.my_leave_menu_item = (By.XPATH, '//a[text()="My Leave"]')
        self.leave_list_menu_item = (By.XPATH, '//a[text()="Leave List"]')

    def is_leave_page_displayed(self):
        return super().is_displayed(self.leave)

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

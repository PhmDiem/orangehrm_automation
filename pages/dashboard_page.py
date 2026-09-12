from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Navigation locators ---
        self.upgrade_btn = (
            By.XPATH,
            '//button[@class="oxd-glass-button orangehrm-upgrade-button"]',
        )
        self.admin_btn = (
            By.XPATH,
            '//a[contains(@href, "/admin/viewAdminModule")]',
        )
        self.pim_btn = (
            By.XPATH,
            '//a[contains(@href, "/pim/viewPimModule")]',
        )

        self.leave_btn = (
            By.XPATH,
            '//a[contains(@href, "/leave/viewLeaveModule")]',
        )

        self.my_info_btn = (
            By.XPATH,
            '//a[contains(@href, "/pim/viewMyDetails")]',
        )

    # --- Verification ---

    def is_upgrade_button_displayed(self):
        return self.is_displayed(self.upgrade_btn)

    # --- Navigation ---

    def ensure_expected_locale(self):
        """Repair locale changes made by an earlier test before continuing."""
        from pages.admin.configuration.localization_page import LocalizationPage

        return LocalizationPage(self.driver).ensure_expected_locale()

    def navigate_to_admin_page(self):
        self.click(self.admin_btn)

    def navigate_to_pim_page(self):
        self.click(self.pim_btn)

    def navigate_to_leave_page(self):
        self.click(self.leave_btn)

    def navigate_to_my_info_page(self):
        self.click(self.my_info_btn)

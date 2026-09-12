from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LocalizationPage(BasePage):
    """Read and restore the locale required by date-sensitive UI tests."""

    EXPECTED_LANGUAGE = "English (United States)"
    EXPECTED_DATE_FORMAT = "yyyy-dd-mm"

    admin_link = (By.XPATH, "//a[contains(@href, '/admin/viewAdminModule')]")
    configuration_menu = (
        By.XPATH,
        "(//li[contains(@class, 'oxd-topbar-body-nav-tab') "
        "and contains(@class, '--parent')])[last()]",
    )
    localization_link = (
        By.XPATH,
        "//li[.//span[contains(@class, 'oxd-topbar-body-nav-tab-item')]"
        " and .//i[contains(@class, 'bi-chevron-down')]]"
        "/ul[contains(@class, 'oxd-dropdown-menu')][1]/li[3]/a",
    )
    language_dropdown = (
        By.XPATH,
        "(//form[contains(@class, 'oxd-form')]"
        "//div[contains(@class, 'oxd-input-group')])[1]"
        "//div[contains(@class, 'oxd-select-text-input')]",
    )
    date_format_dropdown = (
        By.XPATH,
        "(//form[contains(@class, 'oxd-form')]"
        "//div[contains(@class, 'oxd-input-group')])[2]"
        "//div[contains(@class, 'oxd-select-text-input')]",
    )
    save_button = (By.XPATH, "//form[contains(@class, 'oxd-form')]//button[@type='submit']")
    language_option = (
        By.XPATH,
        "//div[@role='option'][.//span[normalize-space()='English (United States)']]",
    )
    date_format_option = (
        By.XPATH,
        "//div[@role='option'][starts-with(normalize-space(), 'yyyy-dd-mm')]",
    )

    def ensure_expected_locale(self):
        """Restore the expected locale if a preceding test changed it.

        The caller's route is restored even when the locale is already correct,
        so this guard can safely run before normal module navigation.
        """
        original_url = self.driver.current_url
        self._open_localization()
        try:
            self.wait.until(
                lambda driver: driver.find_elements(*self.language_dropdown)
                and driver.find_elements(*self.date_format_dropdown)
            )
            changed = self._select_if_needed(
                self.language_dropdown,
                self.EXPECTED_LANGUAGE,
                self.language_option,
            )
            changed = self._select_if_needed(
                self.date_format_dropdown,
                self.EXPECTED_DATE_FORMAT,
                self.date_format_option,
            ) or changed
            if changed:
                self.click(self.save_button)
                self.wait_for_loading_to_disappear()
            return changed
        finally:
            self.driver.get(original_url)
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )

    def _open_localization(self):
        self.wait.until(lambda driver: driver.find_elements(*self.admin_link))
        self.click(self.admin_link)
        self.click(self.configuration_menu)
        self.click_via_js(self.localization_link)

    def _select_if_needed(self, dropdown, expected_value, option):
        if self.get_text(dropdown).strip() == expected_value:
            return False
        self.click(dropdown)
        self.click(option)
        return True

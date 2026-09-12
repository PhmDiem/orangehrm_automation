from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class UserManagementPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Page and table locators ---
        self.system_users = (By.XPATH, '//h5[text()="System Users"]')
        self.users_list = (By.XPATH, '//div[@class="oxd-table"]')
        self.user_rows = (By.CSS_SELECTOR, ".oxd-table .oxd-table-card")
        self.add_btn = (
            By.XPATH,
            '//button[@class="oxd-button oxd-button--medium oxd-button--secondary"]',
        )
        self.user_role = (
            By.XPATH,
            '//label[text()="User Role"]/following::div[1]',
        )
        self.employee_name = (By.XPATH, '//p[@class="oxd-userdropdown-name"]')
        self.input_employee_name = (
            By.XPATH,
            '//input[@placeholder="Type for hints..."]',
        )
        self.option_employee = (
            By.XPATH,
            '//div[@class="oxd-autocomplete-option"]/span',
        )
        self.status = (By.XPATH, '//label[text()="Status"]/following::div[1]')
        self.search_btn = (By.XPATH, '//button[@type="submit"]')
        self.result_rows = (
            By.XPATH,
            '//div[@class="oxd-table-body"]//div[@role="row"]',
        )
        self.input_username_search = (
            By.XPATH,
            '//label[text()="Username"]/following::input[1]',
        )
        self.no_records_msg = (By.XPATH, '//span[text()="No Records Found"]')
        self.table_loader = (By.CSS_SELECTOR, ".oxd-table-loader")
        self.confirm_delete_btn = (
            By.XPATH,
            '//button[normalize-space()="Yes, Delete"]',
        )
        self.bulk_delete_btn = (
            By.XPATH,
            '//button[text()=" Delete Selected "]',
        )
        self.selected_records_count = (
            By.XPATH,
            "//*[contains(normalize-space(.), 'Selected')]",
        )

    # --- Page state ---

    def is_user_management_displayed(self):
        return self.is_displayed(self.system_users)

    def is_users_list_displayed(self):
        return self.is_displayed(self.users_list)

    def get_user_row_count(self):
        return len(self.find_elements(self.user_rows))

    def navigate_to_add_user(self):
        self.click(self.add_btn)

    # --- Search and filter actions ---

    def select_user_role(self, role):
        self.click(self.user_role)
        self.click(
            (
                By.XPATH,
                f'//div[@class="oxd-select-option"]/span[text()="{role}"]',
            )
        )

    def select_employee(self):
        employee_name = self.get_text(self.employee_name)
        self.send_keys(self.input_employee_name, employee_name)
        self.click_dropdown_option(self.option_employee)

    def select_status(self, status):
        self.click(self.status)
        self.click(
            (
                By.XPATH,
                f'//div[@class="oxd-select-option"]/span[text()="{status}"]',
            )
        )

    def click_search_btn(self):
        self.click(self.search_btn)
        self.wait_for_search_results()

    def wait_for_search_results(self):
        return self.wait_for_table_result(
            self.result_rows,
            self.no_records_msg,
        )

    def get_user_row_text(self, username):
        def find_matching_row(driver):
            try:
                rows = driver.find_elements(*self.result_rows)
                for row in rows:
                    row_text = row.text
                    if username in row_text:
                        return row_text
            except StaleElementReferenceException:
                return False
            return False

        return self.wait.until(find_matching_row)

    # --- Search verification ---

    def enter_username_search(self, username):
        self.send_keys(self.input_username_search, username)

    def is_no_records_found_displayed(self):
        return self.is_element_visible(
            self.no_records_msg,
            timeout=ConfigReader.get_timeout("feedback"),
        )

    def wait_for_no_records_found(self):
        return self.wait_for_empty_table(
            self.result_rows,
            self.no_records_msg,
        )

    def click_user_row(self, username):
        row_link = (
            By.XPATH,
            f'//div[@role="row"][.//div[text()="{username}"]]//i[@class="oxd-icon bi-pencil-fill"]',
        )

        def click_fresh_row_link(driver):
            try:
                element = driver.find_element(*row_link)
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(click_fresh_row_link)

    # --- Delete actions ---

    def delete_user_row(self, username):
        delete_icon = (
            By.XPATH,
            f'//div[@role="row"][.//div[text()="{username}"]]//i[@class="oxd-icon bi-trash"]',
        )
        self.click(delete_icon)

    def confirm_delete(self):
        self.confirm_delete_dialog(self.confirm_delete_btn)

    def select_checkbox(self, username):
        checkbox_locator = (
            By.XPATH,
            f'//div[@role="row"][.//*[normalize-space(text())="{username}"]]'
            f'//input[@type="checkbox"]',
        )

        def click_fresh_checkbox(driver):
            try:
                checkbox = driver.find_element(*checkbox_locator)
                if checkbox.is_enabled():
                    driver.execute_script("arguments[0].click();", checkbox)
                    return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(click_fresh_checkbox)

    def click_bulk_delete_btn(self):
        self.click(self.bulk_delete_btn)

    def wait_for_selected_records(self, expected_count):
        """Wait until the bulk-selection toolbar confirms the selected count."""
        noun = "Record" if expected_count == 1 else "Records"
        expected_text = f"({expected_count}) {noun} Selected"
        return WebDriverWait(
            self.driver, ConfigReader.get_timeout("feedback")
        ).until(
            lambda driver: any(
                expected_text in element.text
                for element in driver.find_elements(*self.selected_records_count)
            )
        )

    def is_user_displayed(self, username):
        user_row = (
            By.XPATH,
            f'//div[@role="row"]'
            f'[.//*[normalize-space(text())="{username}"]]',
        )
        return any(
            element.is_displayed()
            for element in self.driver.find_elements(*user_row)
        )

    def wait_for_user_absent(self, username):
        self.wait_for_loading_to_disappear()
        user_row = (
            By.XPATH,
            f'//div[@role="row"]'
            f'[.//*[normalize-space(text())="{username}"]]'
        )
        return WebDriverWait(
            self.driver, ConfigReader.get_timeout("feedback")
        ).until(
            lambda driver: not any(
                element.is_displayed()
                for element in driver.find_elements(*user_row)
            )
        )

    def get_usernames_by_prefix(self, prefix):
        username_cells = (
            By.XPATH,
            f'//div[@role="row"]//*[starts-with(normalize-space(text()), "{prefix}")]',
        )
        return list(
            dict.fromkeys(
                element.text.strip()
                for element in self.find_elements(username_cells)
                if element.text.strip()
            )
        )

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class PIMPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Page and table locators ---
        self.employee_information = (
            By.XPATH,
            '//h5[text()="Employee Information"]',
        )
        self.employees_list = (
            By.CSS_SELECTOR,
            ".oxd-table.orangehrm-employee-list",
        )
        self.employee_rows = (
            By.CSS_SELECTOR,
            ".oxd-table.orangehrm-employee-list .oxd-table-card",
        )
        self.add_btn = (
            By.XPATH,
            '//button[@class="oxd-button oxd-button--medium oxd-button--secondary"]',
        )
        self.search_employee_name_input = (
            By.XPATH,
            '//label[text()="Employee Name"]/following::input[1]',
        )
        self.search_employee_id_input = (
            By.XPATH,
            '//label[text()="Employee Id"]/following::input[1]',
        )
        self.search_btn = (By.XPATH, '//button[@type="submit"]')
        self.reset_btn = (By.XPATH, '//button[@type="reset"]')
        self.no_records_text = (By.XPATH, '//span[text()="No Records Found"]')
        self.table_loader = (By.CSS_SELECTOR, ".oxd-table-loader")
        self.autocomplete_option = (By.XPATH, '//div[@role="option"]')
        self.employee_name_link = (
            By.XPATH,
            '//div[contains(@class,"oxd-table-card")][1]//div[@role="row"]',
        )
        self.row_checkbox = (
            By.XPATH,
            '//div[@class="oxd-table-card"]//input[@type="checkbox"]',
        )
        self.delete_selected_btn = (
            By.XPATH,
            '//button[contains(.,"Delete Selected")]',
        )
        self.delete_row_btn = (
            By.XPATH,
            '//div[@class="oxd-table-card"]//i[contains(@class,"bi-trash")]',
        )
        self.confirm_delete_btn = (
            By.XPATH,
            '//button[text()=" Yes, Delete "]',
        )
        self.delete_row_icon = (
            By.XPATH,
            '(//div[@class="oxd-table-card"]//i[contains(@class,"bi-trash")])[1]',
        )

    # --- Page state ---

    def is_employee_information_displayed(self):
        return super().is_displayed(self.employee_information)

    def is_employees_list_displayed(self):
        return super().is_displayed(self.employees_list)

    def get_employee_row_count(self):
        return len(self.find_elements(self.employee_rows))

    def navigate_to_add_employee(self):
        self.click(self.add_btn)

    # --- Search actions and verification ---

    def search_by_employee_name(self, name):
        self.send_keys(self.search_employee_name_input, name)
        self.click_dropdown_option(
            self.autocomplete_option, expected_text=name
        )
        self.click(self.search_btn)
        self.wait_for_search_results()

    def search_by_employee_id(self, employee_id):
        self.send_keys(self.search_employee_id_input, employee_id)
        self.click(self.search_btn)
        self.wait_for_search_results()

    def wait_for_search_results(self):
        return self.wait_for_table_result(
            self.employee_rows,
            self.no_records_text,
        )

    def is_no_records_found_displayed(self):
        return self.is_element_visible(
            self.no_records_text,
            timeout=ConfigReader.get_timeout("feedback"),
        )

    def get_first_row_text(self):
        rows = self.driver.find_elements(*self.employee_rows)
        if not rows:
            raise AssertionError("Expected at least one employee result row")
        return rows[0].text

    def get_employee_row_count_after_search(self):
        self.wait_for_search_results()
        return len(self.driver.find_elements(*self.employee_rows))

    def is_employee_row_displayed(self, employee_name):
        rows = self.driver.find_elements(*self.employee_rows)
        expected_parts = [
            part.casefold()
            for part in employee_name.split()
            if part.strip()
        ]
        return any(
            all(part in row.text.casefold() for part in expected_parts)
            for row in rows
        )

    def wait_for_no_records_found(self):
        return self.wait_for_empty_table(
            self.employee_rows,
            self.no_records_text,
        )

    def wait_for_employee_absent(self, employee_name):
        self.wait_for_loading_to_disappear()
        expected_parts = [
            part.casefold()
            for part in employee_name.split()
            if part.strip()
        ]

        return WebDriverWait(
            self.driver, ConfigReader.get_timeout("feedback")
        ).until(
            lambda driver: not any(
                all(part in row.text.casefold() for part in expected_parts)
                for row in driver.find_elements(*self.employee_rows)
            )
        )

    def click_first_employee_row(self):
        self.click(self.employee_name_link)

    # --- Delete actions ---

    def delete_first_employee_row(self):
        self.click(self.delete_row_btn)

    def confirm_delete(self):
        self.confirm_delete_dialog(self.confirm_delete_btn)

    def click_first_row_checkbox(self):
        row = self.find_elements(self.employee_rows)[0]
        checkbox = row.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
        self.driver.execute_script("arguments[0].click();", checkbox)

    def click_delete_selected(self):
        self.click(self.delete_selected_btn)

    def delete_first_row_with_bulk_action(self):
        self.click_first_row_checkbox()
        self.click_delete_selected()

    def delete_first_row_via_icon(self):
        self.click(self.delete_row_icon)

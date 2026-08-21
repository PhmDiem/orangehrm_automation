from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage

class PIMPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.employee_information = (By.XPATH, '//h5[text()="Employee Information"]')
        self.employees_list = (By.CSS_SELECTOR, '.oxd-table.orangehrm-employee-list')
        self.employee_rows = (By.CSS_SELECTOR, '.oxd-table.orangehrm-employee-list .oxd-table-card')
        self.add_btn = (
            By.XPATH,
            '//button[@class="oxd-button oxd-button--medium oxd-button--secondary"]'
        )
        self.search_employee_name_input = (
            By.XPATH, '//label[text()="Employee Name"]/following::input[1]'
        )
        self.search_employee_id_input = (
            By.XPATH, '//label[text()="Employee Id"]/following::input[1]'
        )
        self.search_btn = (By.XPATH, '//button[@type="submit"]')
        self.reset_btn = (By.XPATH, '//button[@type="reset"]')
        self.no_records_text = (By.XPATH, '//span[text()="No Records Found"]')
        self.autocomplete_option = (By.XPATH, '//div[@role="option"]')
        self.employee_name_link = (
            By.XPATH, '//div[contains(@class,"oxd-table-card")][1]//div[@role="row"]'
        )
        self.row_checkbox = (By.XPATH, '//div[@class="oxd-table-card"]//input[@type="checkbox"]')
        self.delete_selected_btn = (By.XPATH, '//button[contains(.,"Delete Selected")]')
        self.delete_row_btn = (By.XPATH, '//div[@class="oxd-table-card"]//i[contains(@class,"bi-trash")]')
        self.confirm_delete_btn = (By.XPATH, '//button[text()=" Yes, Delete "]')
        self.row_checkbox = (
            By.XPATH, '//div[@class="oxd-table-card"]//input[@type="checkbox"]'
        )
        self.delete_selected_btn = (
            By.XPATH, '//button[contains(.,"Delete Selected")]'
        )
        self.delete_row_icon = (
            By.XPATH, '(//div[@class="oxd-table-card"]//i[contains(@class,"bi-trash")])[1]'
        )
        self.confirm_delete_btn = (By.XPATH, '//button[text()=" Yes, Delete "]')
        

    def is_employee_information_displayed(self):
        return super().is_displayed(self.employee_information)

    def is_employees_list_displayed(self):
        return super().is_displayed(self.employees_list)

    def get_employee_row_count(self):
        return len(self.find_elements(self.employee_rows))

    def navigate_to_add_employee(self):
        self.click(self.add_btn)

    def search_by_employee_name(self, name):
        self.send_keys(self.search_employee_name_input, name)
        self.click_dropdown_option(self.autocomplete_option, expected_text=name)
        self.click(self.search_btn)

    def search_by_employee_id(self, employee_id):
        self.send_keys(self.search_employee_id_input, employee_id)
        self.click(self.search_btn)

    def is_no_records_found_displayed(self):
        return self.is_element_visible(
            self.no_records_text,
            timeout=5
        )

    def get_first_row_text(self):
        rows = self.find_elements(self.employee_rows)
        return rows[0].text if rows else ""

    def get_employee_row_count_after_search(self):
        try:
            return len(self.driver.find_elements(*self.employee_rows))
        except Exception:
            return 0

    def click_first_employee_row(self):
        self.click(self.employee_name_link)

    def delete_first_employee_row(self):
        self.click(self.delete_row_btn)

    def confirm_delete(self):
        self.click(self.confirm_delete_btn)

    def click_first_row_checkbox(self):
        self.click_via_js(self.row_checkbox)

    def click_delete_selected(self):
        self.click(self.delete_selected_btn)

    def delete_first_row_via_icon(self):
        self.click(self.delete_row_icon)

    def confirm_delete(self):
        self.click(self.confirm_delete_btn)
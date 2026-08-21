from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage

class UserManagementPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.system_users = (By.XPATH, '//h5[text()="System Users"]')
        self.users_list = (By.XPATH, '//div[@class="oxd-table"]')
        self.user_rows = (By.CSS_SELECTOR, '.oxd-table .oxd-table-card')
        self.add_btn = (
            By.XPATH,
            '//button[@class="oxd-button oxd-button--medium oxd-button--secondary"]'
        )
        self.user_role = (By.XPATH, '//label[text()="User Role"]/following::div[1]')
        self.employee_name = (By.XPATH, '//p[@class="oxd-userdropdown-name"]')
        self.input_employee_name = (By.XPATH, '//input[@placeholder="Type for hints..."]')
        self.option_employee = (
            By.XPATH,
            '//div[@class="oxd-autocomplete-option"]/span'
        )
        self.status = (By.XPATH, '//label[text()="Status"]/following::div[1]')
        self.search_btn = (By.XPATH, '//button[@type="submit"]')
        self.result_rows = (By.XPATH, '//div[@class="oxd-table-body"]//div[@role="row"]')
        self.input_username_search = (
            By.XPATH,
            '//label[text()="Username"]/following::input[1]'
        )
        self.no_records_msg = (By.XPATH, '//span[text()="No Records Found"]')
        self.confirm_delete_btn = (By.XPATH, '//button[text()=" Yes, Delete "]')
        self.bulk_delete_btn = (By.XPATH, '//button[text()=" Delete Selected "]')

    def is_user_management_displayed(self):
        return self.is_displayed(self.system_users)

    def is_users_list_displayed(self):
        return self.is_displayed(self.users_list)

    def get_user_row_count(self):
        return len(self.find_elements(self.user_rows))
    
    def navigate_to_add_user(self):
        self.click(self.add_btn) 

    def select_user_role(self, role):
        self.click(self.user_role)
        self.click((By.XPATH, f'//div[@class="oxd-select-option"]/span[text()="{role}"]'))

    def select_employee(self):
        employee_name = self.get_text(self.employee_name)
        self.send_keys(self.input_employee_name, employee_name)
        self.click_dropdown_option(self.option_employee)

    def select_status(self, status):
        self.click(self.status)
        self.click((By.XPATH, f'//div[@class="oxd-select-option"]/span[text()="{status}"]')) 

    def click_search_btn(self):
        self.click(self.search_btn)

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

    def enter_username_search(self, username):
        self.send_keys(self.input_username_search, username)

    def is_no_records_found_displayed(self):
        return self.is_displayed(self.no_records_msg)

    def click_user_row(self, username):
        row_link = (By.XPATH, f'//div[@role="row"][.//div[text()="{username}"]]//i[@class="oxd-icon bi-pencil-fill"]')

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

    def delete_user_row(self, username):
        delete_icon = (By.XPATH, f'//div[@role="row"][.//div[text()="{username}"]]//i[@class="oxd-icon bi-trash"]')
        self.click(delete_icon)

    def confirm_delete(self):
        self.click(self.confirm_delete_btn)

    def select_checkbox(self, username):
        checkbox_locator = (
            By.XPATH,
            f'//div[@role="row"][.//*[normalize-space(text())="{username}"]]'
            f'//input[@type="checkbox"]'
        )
        checkbox = self.find_element(checkbox_locator)
        self.driver.execute_script("arguments[0].click();", checkbox)

    def click_bulk_delete_btn(self):
        self.click(self.bulk_delete_btn)

    def is_user_displayed(self, username):
        user_row = (
            By.XPATH,
            f'//div[@role="row"]'
            f'[.//*[normalize-space(text())="{username}"]]'
        )
        return self.is_element_visible(user_row)

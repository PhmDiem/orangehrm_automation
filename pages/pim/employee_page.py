from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class EmployeePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.employee_information = (
            By.XPATH,
            '//h5[normalize-space()="Employee Information"]',
        )
        self.employees_list = (
            By.CSS_SELECTOR,
            '.oxd-table.orangehrm-employee-list',
        )

    def is_employee_information_displayed(self):
        return super().is_displayed(self.employee_information)

    def is_employees_list_displayed(self):
        return super().is_displayed(self.employees_list)
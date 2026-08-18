from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class AddUserPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.user_role= (By.XPATH, '//label[text()="User Role"]/following::div[1]')
        self.employee_name= (By.XPATH, '//p[@class="oxd-userdropdown-name"]')
        self.input_employee_name= (By.XPATH, '//input[@placeholder="Type for hints..."]')
        self.option_employee= (By.XPATH, '//div[@class="oxd-autocomplete-option"]')
        self.status= (By.XPATH, '//label[text()="Status"]/following::div[1]')
        self.username_field= (By.XPATH, '//label[text()="Username"]/following::input[1]')
        self.password_field= (By.XPATH, '//label[text()="Password"]/following::input[1]')
        self.confirm_password_field= (By.XPATH, '//label[text()="Confirm Password"]/following::input[1]')
        self.save_btn= (By.XPATH, '//button[@type="submit"]')
        self.username_error = (By.XPATH, '//span[text()="Already exists"]')
        self.required_error_message= (By.XPATH, '//span[text()="Required"]')

    def select_user_role(self, role):
        self.click(self.user_role)
        self.click((By.XPATH, f'//div[@class="oxd-select-option"]/span[text()="{role}"]'))    

    def select_employee(self):
        self.get_employee_name = self.get_text(self.employee_name)
        self.send_keys(self.input_employee_name, self.get_employee_name)
        self.click_dropdown_option(self.option_employee)

    def select_status(self, status):
        self.click(self.status)
        self.click((By.XPATH, f'//div[@class="oxd-select-option"]/span[text()="{status}"]')) 

    def enter_username(self, username):
        self.send_keys(self.username_field, username) 

    def enter_password(self, password):
        self.send_keys(self.password_field, password) 

    def enter_confirm_password(self, password):
        self.send_keys(self.confirm_password_field, password)  

    def click_save_btn(self):
        self.click(self.save_btn) 

    def create_user(self, role, status, username, password):
        self.select_user_role(role)
        self.select_employee()
        self.select_status(status)
        self.enter_username(username)
        self.enter_password(password)
        self.enter_confirm_password(password)
        self.click_save_btn()    

    def get_username_error_text(self):
        return self.get_text(self.username_error)

    def is_username_error_displayed(self):
        return self.is_displayed(self.username_error)

    def create_user_without_username(self, role, status, password):
        self.select_user_role(role)
        self.select_employee()
        self.select_status(status)
        self.enter_password(password)
        self.enter_confirm_password(password)
        self.click_save_btn()

    def get_required_error_text(self):
        return self.get_text(self.required_error_message)

    def is_required_error_displayed(self):
        return self.is_displayed(self.required_error_message)

    

    








        
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains

class UserManagementPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        self.user_list= (By.XPATH, '//div[@class="oxd-table"]')
        self.add_btn= (By.XPATH, '//button[@class="oxd-button oxd-button--medium oxd-button--secondary"]')
        self.user_role= (By.XPATH, '//label[text()="User Role"]/following::div[1]')
        self.employee_name= (By.XPATH, '//p[@class="oxd-userdropdown-name"]')
        self.input_employee_name= (By.XPATH, '//input[@placeholder="Type for hints..."]')
        self.option_employee= (By.XPATH, '//div[@class="oxd-autocomplete-option"]')
        self.status= (By.XPATH, '//label[text()="Status"]/following::div[1]')
        self.username_field= (By.XPATH, '//label[text()="Username"]/following::input[1]')
        self.password_field= (By.XPATH, '//label[text()="Password"]/following::input[1]')
        self.confirm_password_field= (By.XPATH, '//label[text()="Confirm Password"]/following::input[1]')
        self.save_btn= (By.XPATH, '//button[@type="submit"]')

    def is_user_list_displayed(self):
        return self.is_displayed(self.user_list)
    
    def navigate_to_add_user(self):
        self.click(self.add_btn)

    def select_user_role(self, role):
        self.click(self.user_role)
        self.click((By.XPATH, f'//div[@class="oxd-select-option"]/span[text()="{role}"]'))    

    def select_employee(self):
        get_employee_name = self.get_text(self.employee_name)
        self.send_keys(self.input_employee_name, get_employee_name)
        actionchain = ActionChains(self.driver)
        wait_option = self.wait_to_presence(self.option_employee)
        actionchain.move_to_element(wait_option).pause(3).click().perform()

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








        
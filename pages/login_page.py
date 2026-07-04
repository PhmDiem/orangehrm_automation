from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver=driver

        self.login_title= (By.XPATH, '//h5[@class="oxd-text oxd-text--h5 orangehrm-login-title"]')
        self.username_field= (By.NAME, 'username')
        self.password_field= (By.NAME, 'password')
        self.click_btn= (By.XPATH, '//button[@type="submit"]')
        self.Invalid_error_message= (By.XPATH, '//p[@class="oxd-text oxd-text--p oxd-alert-content-text"]')
        self.required_error_message= (By.XPATH, '//span[@class="oxd-text oxd-text--span oxd-input-field-error-message oxd-input-group__message"]')
        self.user_dropdown= (By.XPATH, '//span[@class="oxd-userdropdown-tab"]')
        self.logout_btn= (By.XPATH, '//a[text()="Logout"]')

    def login(self, username, password):
        self.send_keys(self.username_field, username)
        self.send_keys(self.password_field, password)
        self.click(self.click_btn)
    
    def is_login_displayed(self):
        return self.is_displayed(self.login_title)

    def get_error_message(self):
        if self.is_element_visible(self.Invalid_error_message):
            return self.get_text(self.Invalid_error_message)
        else:
            return self.get_text(self.required_error_message)
        
    def logout(self):
        self.click(self.user_dropdown)    
        self.click(self.logout_btn)

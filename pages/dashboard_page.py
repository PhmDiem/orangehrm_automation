from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class DashboardPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver=driver

        self.upgrade_btn= (By.XPATH, '//button[@class="oxd-glass-button orangehrm-upgrade-button"]')
        self.admin_btn= (By.XPATH, '//a[@href="/web/index.php/admin/viewAdminModule"]')

    def is_upgrade_button_displayed(self):
        return self.is_displayed(self.upgrade_btn)
    
    def navigate_to_admin_page(self):
        self.click(self.admin_btn)
        
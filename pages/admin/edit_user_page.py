from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class EditUserPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # --- Form locators ---
        self.user_role = (
            By.XPATH,
            '//label[text()="User Role"]/following::div[1]',
        )
        self.save_btn = (By.XPATH, '//button[@type="submit"]')

    # --- Actions ---

    def select_user_role(self, role):
        self.click(self.user_role)
        self.click(
            (
                By.XPATH,
                f'//div[@class="oxd-select-option"]/span[text()="{role}"]',
            )
        )

    def click_save_btn(self):
        self.click(self.save_btn)

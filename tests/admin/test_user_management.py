import pytest
import random
from utils.config_reader import ConfigReader
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.admin.user_management_page import UserManagementPage
from time import sleep

class TestUserManagement:
    @pytest.mark.admin
    def test_user_management(self, driver):
        login_page = LoginPage(driver)
        user = ConfigReader.get_user("admin")
        login_page.login(user["username"], user["password"])

        dashboard_page = DashboardPage(driver)
        dashboard_page.navigate_to_admin_page()

        user_management_page = UserManagementPage(driver)
        user_management_page.navigate_to_add_user()
        user_management_page.select_user_role("ESS")
        user_management_page.select_employee()
        user_management_page.select_status("Enabled")
        username = f"test_user_{random.randint(1, 1000)}"
        user_management_page.enter_username(username)
        user_management_page.enter_password("Test@123")
        user_management_page.enter_confirm_password("Test@123")
        user_management_page.click_save_btn()

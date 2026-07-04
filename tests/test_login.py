import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.config_reader import ConfigReader
import allure

@pytest.mark.login
class TestLogin:
    def test_login_success(self, driver):
        login_page= LoginPage(driver)
        user = ConfigReader.get_user("admin")
        login_page.login(user["username"], user["password"])

        dashboard_page = DashboardPage(driver)
        dashboard_page.is_upgrade_button_displayed()

    @pytest.mark.smoke
    @pytest.mark.parametrize("user_type, expected_error", [
    ("wrong_username", "Invalid credentials"),
    ("wrong_password", "Invalid credentials"),
    ("wrong_both",     "Invalid credentials"),
    ("empty_username", "Required"),
    ("empty_password", "Required"),
    ])
    def test_login_fail(self, driver, user_type, expected_error):
        login_page = LoginPage(driver)
        user = ConfigReader.get_user(user_type)
        login_page.login(user["username"], user["password"])
        assert login_page.get_error_message() == expected_error    

    @pytest.mark.logout
    def test_logout(self, driver):
        login_page = LoginPage(driver)
        user = ConfigReader.get_user("admin")
        login_page.login(user["username"], user["password"])
        login_page.logout()    
        assert login_page.is_login_displayed() 
        
    
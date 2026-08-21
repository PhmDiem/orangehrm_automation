import allure
import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.config_reader import ConfigReader


@pytest.mark.login
class TestLogin:

    @allure.title("Login successfully with valid admin credentials")
    def test_login_success(self, driver):
        login_page = LoginPage(driver)

        with allure.step("Login with valid admin credentials"):
            user = ConfigReader.get_user("admin")
            login_page.login(user["username"], user["password"])

        with allure.step("Verify Dashboard is displayed"):
            dashboard_page = DashboardPage(driver)
            assert dashboard_page.is_upgrade_button_displayed()

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "user_type, expected_error",
        [
            ("wrong_username", "Invalid credentials"),
            ("wrong_password", "Invalid credentials"),
            ("wrong_both", "Invalid credentials"),
            ("empty_username", "Required"),
            ("empty_password", "Required"),
            ("empty_both", "Required"),
        ],
    )
    @allure.title("Login failed with {user_type} credentials")
    def test_login_fail(self, driver, user_type, expected_error):
        login_page = LoginPage(driver)

        with allure.step(f"Login with {user_type} credentials"):
            user = ConfigReader.get_user(user_type)
            login_page.login(user["username"], user["password"])

        with allure.step(f"Verify error message: {expected_error}"):
            assert login_page.get_error_message() == expected_error

    @pytest.mark.logout
    @allure.title("Logout successfully")
    def test_logout(self, driver):
        login_page = LoginPage(driver)

        with allure.step("Login with valid admin credentials"):
            user = ConfigReader.get_user("admin")
            login_page.login(user["username"], user["password"])

        with allure.step("Logout from the application"):
            login_page.logout()

        with allure.step("Verify Login page is displayed"):
            assert login_page.is_login_displayed()

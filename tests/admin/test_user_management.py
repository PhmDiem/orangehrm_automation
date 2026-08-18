import allure
import pytest

from utils.test_data import TestData
from pages.dashboard_page import DashboardPage
from pages.admin.user_management_page import UserManagementPage
from pages.admin.add_user_page import AddUserPage
from pages.admin.edit_user_page import EditUserPage


@pytest.mark.admin
class TestUserManagement:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.user_management_page = UserManagementPage(driver)
        self.add_user_page = AddUserPage(driver)
        self.edit_user_page = EditUserPage(driver)

    @allure.title("View list of users")
    def test_view_list_of_users(self):
        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Verify user list is displayed"):
            assert self.user_management_page.is_users_list_displayed(), \
                "User list is not displayed"

    @pytest.mark.new_user
    @allure.title("Create a new ESS user")
    def test_create_new_user(self):
        username = TestData.generate_username()

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step(f"Create new ESS user: {username}"):
            self.add_user_page.create_user(
                "ESS",
                "Enabled",
                username,
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step("Search for the newly created user"):
            self.user_management_page.select_employee()
            self.user_management_page.select_status("Enabled")
            self.user_management_page.click_search_btn()

        with allure.step("Verify user appears in search results"):
            self.user_management_page.verify_search_results(
                username=username,
                role="ESS"
            )

    @pytest.mark.duplicate
    @allure.title("Create user with duplicate username")
    def test_create_duplicate_username(self):
        username = TestData.generate_username()

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Create the first user"):
            self.user_management_page.navigate_to_add_user()
            self.add_user_page.create_user(
                "ESS",
                "Enabled",
                username,
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step("Attempt to create user with duplicate username"):
            self.user_management_page.navigate_to_add_user()
            self.add_user_page.create_user(
                "ESS",
                "Enabled",
                username,
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify duplicate username error is displayed"):
            assert self.add_user_page.is_username_error_displayed()

        with allure.step("Verify error message contains 'Already exists'"):
            assert "Already exists" in self.add_user_page.get_username_error_text()

    @pytest.mark.required
    @allure.title("Create user without username")
    def test_create_user_without_username(self):

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step("Create user without username"):
            self.add_user_page.create_user_without_username(
                "ESS",
                "Enabled",
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify required error is displayed"):
            assert self.add_user_page.is_required_error_displayed()

        with allure.step("Verify error message contains 'Required'"):
            assert "Required" in self.add_user_page.get_required_error_text()

    @pytest.mark.search_by_username
    @allure.title("Search for user by username")
    def test_search_by_username(self):
        username = TestData.generate_username()

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step(f"Create new ESS user: {username}"):
            self.add_user_page.create_user(
                "ESS",
                "Enabled",
                username,
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step(f"Search for user by username: {username}"):
            self.user_management_page.enter_username_search(username)
            self.user_management_page.click_search_btn()

        with allure.step("Verify user appears in search results"):
            self.user_management_page.verify_search_results(
                username=username,
                role="ESS"
            )

    @pytest.mark.search_by_role
    @allure.title("Search for user by role")
    def test_search_by_role(self):
        username = TestData.generate_username()

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step(f"Create new ESS user: {username}"):
            self.add_user_page.create_user(
                "ESS", 
                "Enabled", 
                username, 
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step("Search for user by role: ESS"):
            self.user_management_page.select_user_role("ESS")
            self.user_management_page.click_search_btn()

        with allure.step("Verify user appears in search results"):
            self.user_management_page.verify_search_results(username=username, role="ESS")

    @pytest.mark.search_nonexistent
    @allure.title("Search for non-existent user")
    def test_search_nonexistent_user(self):
        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        fake_username = TestData.generate_username(prefix="nonexistent")

        with allure.step(f"Search for non-existent user: {fake_username}"):
            self.user_management_page.enter_username_search(fake_username)
            self.user_management_page.click_search_btn()

        with allure.step("Verify no records found message is displayed"):
            assert self.user_management_page.is_no_records_found_displayed()

    @pytest.mark.edit_user
    @allure.title("Edit user role")
    def test_edit_user_change_role(self):
        username = TestData.generate_username()

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step(f"Create new ESS user: {username}"):
            self.add_user_page.create_user(
                "ESS",
                "Enabled",
                username,
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step(f"Search for user: {username}"):
            self.user_management_page.enter_username_search(username)
            self.user_management_page.click_search_btn()

        with allure.step(f"Open user for editing: {username}"):
            self.user_management_page.click_user_row(username)

        with allure.step("Change user role to Admin"):
            self.edit_user_page.select_user_role("Admin")
            self.edit_user_page.click_save_btn()

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step(f"Search for updated user: {username}"):
            self.user_management_page.enter_username_search(username)
            self.user_management_page.click_search_btn()

        with allure.step("Verify user role has been changed to Admin"):
            self.user_management_page.verify_search_results(
                username=username,
                role="Admin"
            )

    @pytest.mark.delete_user
    @allure.title("Delete single user")
    def test_delete_single_user(self):
        username = TestData.generate_username()

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step(f"Create new ESS user: {username}"):
            self.add_user_page.create_user(
                "ESS",
                "Enabled",
                username,
                TestData.DEFAULT_PASSWORD
            )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step(f"Search for user: {username}"):
            self.user_management_page.enter_username_search(username)
            self.user_management_page.click_search_btn()

        with allure.step(f"Delete user: {username}"):
            self.user_management_page.delete_user_row(username)

        with allure.step("Confirm user deletion"):
            self.user_management_page.confirm_delete()

        with allure.step(f"Search for deleted user: {username}"):
            self.user_management_page.enter_username_search(username)
            self.user_management_page.click_search_btn()

        with allure.step("Verify deleted user is no longer found"):
            assert self.user_management_page.is_no_records_found_displayed()

    @pytest.mark.bulk_delete_users
    @allure.title("Bulk delete users")
    def test_bulk_delete_users(self):

        with allure.step("Navigate to Admin page"):
            self.dashboard_page.navigate_to_admin_page()

        usernames = []

        with allure.step("Create 2 users"):
            for _ in range(2):
                username = TestData.generate_username()
                usernames.append(username)

                self.user_management_page.navigate_to_add_user()
                self.add_user_page.create_user(
                    "ESS",
                    "Enabled",
                    username,
                    TestData.DEFAULT_PASSWORD
                )

        with allure.step("Verify User Management page is displayed"):
            assert self.user_management_page.is_user_management_displayed()

        with allure.step("Select created users for deletion"):
            for username in usernames:
                with allure.step(f"Verify user is displayed: {username}"):
                    assert self.user_management_page.is_user_displayed(username), \
                        f"User '{username}' is not displayed in current table"

        with allure.step("Select checkboxes for created users"):
            for username in usernames:
                self.user_management_page.select_checkbox(username)

        with allure.step("Delete selected users"):
            self.user_management_page.click_bulk_delete_btn()

        with allure.step("Confirm user deletion"):
            self.user_management_page.confirm_delete()

        with allure.step("Verify deleted users are no longer displayed"):
            for username in usernames:
                assert not self.user_management_page.is_user_displayed(username), \
                    f"User '{username}' is still displayed"
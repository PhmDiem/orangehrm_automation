import allure
import pytest

from pages.admin.add_user_page import AddUserPage
from pages.admin.edit_user_page import EditUserPage
from pages.admin.user_management_page import UserManagementPage
from pages.dashboard_page import DashboardPage
from utils.config_reader import ConfigReader
from utils.test_data import TestData


@pytest.mark.admin
class TestUserManagement:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.user_management_page = UserManagementPage(driver)
        self.add_user_page = AddUserPage(driver)
        self.edit_user_page = EditUserPage(driver)

    @pytest.fixture
    def created_users(self, request):
        usernames = []

        def cleanup():
            cleanup_errors = []

            for username in usernames:
                try:
                    self._navigate_to_admin()
                    self._search_user_by_username(username)

                    if self.user_management_page.is_user_displayed(username):
                        self.user_management_page.delete_user_row(username)
                        self.user_management_page.confirm_delete()
                except Exception as error:
                    cleanup_errors.append((username, error))

            if cleanup_errors:
                usernames_with_errors = ", ".join(
                    username for username, _ in cleanup_errors
                )
                raise AssertionError(
                    f"Failed to clean up created users: {usernames_with_errors}"
                ) from cleanup_errors[0][1]

        request.addfinalizer(cleanup)
        return usernames

    def _navigate_to_admin(self):
        self.dashboard_page.navigate_to_admin_page()

    def _create_user(self, username, role=TestData.DEFAULT_ROLE):
        self.user_management_page.navigate_to_add_user()
        self.add_user_page.create_user(
            role,
            TestData.DEFAULT_STATUS,
            username,
            ConfigReader.get_test_user_password(),
        )

    def _create_user_data(self):
        return TestData.generate_username()

    def _search_user_by_username(self, username):
        self.user_management_page.enter_username_search(username)
        self.user_management_page.click_search_btn()

    def _search_user_by_role(self, role):
        self.user_management_page.select_user_role(role)
        self.user_management_page.click_search_btn()

    def _verify_user_management_displayed(self):
        assert (
            self.user_management_page.is_user_management_displayed()
        ), "User Management page is not displayed"

    def _create_and_verify_user(self, username, role=TestData.DEFAULT_ROLE):
        self._create_user(username, role)
        self._verify_user_management_displayed()

    @pytest.mark.view_users
    @allure.title("View list of users")
    def test_view_list_of_users(self):
        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step("Verify user list is displayed"):
            assert (
                self.user_management_page.is_users_list_displayed()
            ), "User list is not displayed"

        with allure.step("Verify at least one user record exists"):
            assert (
                self.user_management_page.get_user_row_count() > 0
            ), "User list is empty"

    @pytest.mark.new_user
    @allure.title("Create a new ESS user")
    def test_create_new_user(self, created_users):
        username = self._create_user_data()
        created_users.append(username)

        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step(f"Create new ESS user: {username}"):
            self._create_and_verify_user(username)

        with allure.step("Search for the newly created user"):
            self.user_management_page.select_employee()
            self.user_management_page.select_status(TestData.DEFAULT_STATUS)
            self.user_management_page.click_search_btn()

        with allure.step("Verify user appears in search results"):
            row_text = self.user_management_page.get_user_row_text(username)
            assert TestData.DEFAULT_ROLE in row_text

    @pytest.mark.duplicate
    @allure.title("Create user with duplicate username")
    def test_create_duplicate_username(self, created_users):
        username = self._create_user_data()
        created_users.append(username)

        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step("Create the first user"):
            self._create_and_verify_user(username)

        with allure.step("Attempt to create user with duplicate username"):
            self._create_user(username)

        with allure.step("Verify duplicate username error is displayed"):
            assert self.add_user_page.is_username_error_displayed()

        with allure.step("Verify error message contains 'Already exists'"):
            assert (
                "Already exists"
                in self.add_user_page.get_username_error_text()
            )

    @pytest.mark.required
    @allure.title("Create user without username")
    def test_create_user_without_username(self):
        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step("Navigate to Add User page"):
            self.user_management_page.navigate_to_add_user()

        with allure.step("Create user without username"):
            self.add_user_page.create_user_without_username(
                TestData.DEFAULT_ROLE,
                TestData.DEFAULT_STATUS,
                ConfigReader.get_test_user_password(),
            )

        with allure.step("Verify required error is displayed"):
            assert self.add_user_page.is_required_error_displayed()

        with allure.step("Verify error message contains 'Required'"):
            assert "Required" in self.add_user_page.get_required_error_text()

    @pytest.mark.search_by_username
    @allure.title("Search for user by username")
    def test_search_by_username(self, created_users):
        username = self._create_user_data()
        created_users.append(username)

        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step(f"Create new ESS user: {username}"):
            self._create_and_verify_user(username)

        with allure.step(f"Search for user by username: {username}"):
            self._search_user_by_username(username)

        with allure.step("Verify user appears in search results"):
            row_text = self.user_management_page.get_user_row_text(username)
            assert TestData.DEFAULT_ROLE in row_text

    @pytest.mark.search_by_role
    @pytest.mark.parametrize("role", [TestData.DEFAULT_ROLE, "Admin"])
    @allure.title("Search for user by role")
    def test_search_by_role(self, created_users, role):
        username = self._create_user_data()
        created_users.append(username)

        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step(f"Create new {role} user: {username}"):
            self._create_and_verify_user(username, role)

        with allure.step(f"Search for user by role: {role}"):
            self._search_user_by_role(role)

        with allure.step("Verify user appears in search results"):
            row_text = self.user_management_page.get_user_row_text(username)
            assert username in row_text
            assert role in row_text

    @pytest.mark.search_nonexistent
    @allure.title("Search for non-existent user")
    def test_search_nonexistent_user(self):
        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        fake_username = TestData.generate_username(prefix="nonexistent")

        with allure.step(f"Search for non-existent user: {fake_username}"):
            self._search_user_by_username(fake_username)

        with allure.step("Verify no records found message is displayed"):
            assert self.user_management_page.is_no_records_found_displayed()

    @pytest.mark.edit_user
    @allure.title("Edit user role")
    def test_edit_user_change_role(self, created_users):
        username = self._create_user_data()
        created_users.append(username)

        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step(f"Create new ESS user: {username}"):
            self._create_and_verify_user(username)

        with allure.step(f"Search for user: {username}"):
            self._search_user_by_username(username)

        with allure.step(f"Open user for editing: {username}"):
            self.user_management_page.click_user_row(username)

        with allure.step("Change user role to Admin"):
            self.edit_user_page.select_user_role("Admin")
            self.edit_user_page.click_save_btn()

        with allure.step("Verify User Management page is displayed"):
            self._verify_user_management_displayed()

        with allure.step(f"Search for updated user: {username}"):
            self._search_user_by_username(username)

        with allure.step("Verify user role has been changed to Admin"):
            row_text = self.user_management_page.get_user_row_text(username)
            assert "Admin" in row_text

    @pytest.mark.delete_user
    @allure.title("Delete single user")
    def test_delete_single_user(self, created_users):
        username = self._create_user_data()
        created_users.append(username)

        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step(f"Create new ESS user: {username}"):
            self._create_and_verify_user(username)

        with allure.step(f"Search for user: {username}"):
            self._search_user_by_username(username)

        with allure.step(f"Delete user: {username}"):
            self.user_management_page.delete_user_row(username)

        with allure.step("Confirm user deletion"):
            self.user_management_page.confirm_delete()

        with allure.step(f"Search for deleted user: {username}"):
            self._search_user_by_username(username)

        with allure.step("Verify deleted user is no longer found"):
            assert self.user_management_page.wait_for_no_records_found(), (
                "Expected No Records Found and an empty user table"
            )
            created_users.remove(username)

    @pytest.mark.bulk_delete_users
    @allure.title("Bulk delete users")
    def test_bulk_delete_users(self, created_users):
        with allure.step("Navigate to Admin page"):
            self._navigate_to_admin()

        with allure.step("Create 2 users for bulk deletion"):
            for _ in range(2):
                username = self._create_user_data()
                created_users.append(username)
                self._create_user(username)

            self._navigate_to_admin()

        with allure.step("Filter users by current employee and ESS role"):
            self.user_management_page.select_employee()
            self.user_management_page.select_user_role(TestData.DEFAULT_ROLE)
            self.user_management_page.click_search_btn()

        with allure.step("Select only test_user accounts"):
            usernames = self.user_management_page.get_usernames_by_prefix(
                "test_user_"
            )
            assert usernames, "No test_user_ accounts were found to delete"
            for username in usernames:
                with allure.step(f"Select checkbox for: {username}"):
                    self.user_management_page.select_checkbox(username)

        with allure.step("Delete selected users"):
            self.user_management_page.click_bulk_delete_btn()

        with allure.step("Confirm user deletion"):
            self.user_management_page.confirm_delete()

        with allure.step("Verify deleted users are no longer displayed"):
            for username in usernames:
                assert self.user_management_page.wait_for_user_absent(
                    username
                ), f"User '{username}' is still displayed"

        # The users were deleted successfully above; do not make the
        # finalizer navigate and attempt to delete them a second time.
        created_users.clear()

import allure
import pytest
from utils.test_data import TestData
from pages.dashboard_page import DashboardPage
from pages.leave.leave_list_page import LeaveListPage
from pages.leave.leave_types_page import LeaveTypesPage
from pages.leave.apply_leave_page import ApplyLeavePage
from pages.leave.my_leave_page import MyLeavePage
from pages.login_page import LoginPage
from utils.config_reader import ConfigReader


@pytest.mark.leave
@pytest.mark.regression
class TestLeaveTypes:

    # --- Fixtures and navigation helpers ---

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.driver = driver
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeaveListPage(driver)
        self.leave_types_page = LeaveTypesPage(driver)

    def _navigate_to_leave(self):
        self.dashboard_page.navigate_to_leave_page()

    @pytest.mark.view_leave_types
    @allure.title("View list of leave types")
    def test_view_list_of_leave_types(self):
        with allure.step("Navigate to Leave page"):
            self._navigate_to_leave()
            assert (
                self.leave_page.is_leave_page_displayed()
            ), "Leave page is not displayed"

        with allure.step("Navigate to Leave Types page"):
            self.leave_page.navigate_to_leave_types()
            assert (
                self.leave_types_page.is_leave_types_page_displayed()
            ), "Leave types page is not displayed"

        with allure.step("Verify employee list is displayed"):
            assert (
                self.leave_types_page.is_leave_types_list_displayed()
            ), "Leave types list is not displayed"

        with allure.step("Verify at least one leave type record exists"):
            assert (
                self.leave_types_page.get_leave_type_row_count() > 0
            ), "Leave types list is empty"

    # --- Apply leave tests ---

@pytest.mark.leave
@pytest.mark.regression
@allure.epic("Leave Management")
@allure.feature("Apply Leave")
class TestApplyLeave:

    # --- Fixtures and navigation helpers ---

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeaveListPage(driver)
        self.apply_leave_page = ApplyLeavePage(driver)
        self.my_leave_page = MyLeavePage(driver)

    def _navigate_to_apply_leave(self):
        self.dashboard_page.navigate_to_leave_page()
        assert self.leave_page.is_leave_page_displayed()
        self.leave_page.navigate_to_apply_leave()
        assert self.apply_leave_page.is_page_displayed()

    @pytest.fixture
    def created_leave_markers(self):
        """Cancel requests registered by a test, even when an assertion fails."""
        markers = []
        yield markers

        if not markers:
            return

        self.dashboard_page.navigate_to_leave_page()
        self.leave_page.navigate_to_my_leave()
        for marker in markers:
            if self.my_leave_page.get_row_by_marker(marker) is not None:
                self.my_leave_page.cancel_leave_by_marker(marker)

    # --- Apply leave tests ---

    @pytest.mark.apply_leave_valid
    @allure.story("TC02 - Apply a valid leave")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_apply_valid_leave_status_pending(
        self, leave_data, ensure_leave_entitlement, created_leave_markers
    ):
        with allure.step("Navigate to Apply Leave"):
            self._navigate_to_apply_leave()

        marker = TestData.generate_unique_marker()
        leave_type = leave_data["valid_leave"]["leave_type"]

        with allure.step("Apply a valid leave request"):
            # Use dynamic dates from date_generator instead of the fixed dates in
            # leave_data, retrying when they overlap a leftover request.
            self.apply_leave_page.apply_leave_avoiding_overlap(
                leave_type=leave_type,
                date_generator=TestData.generate_future_leave_dates,
                comment=marker,
            )
            created_leave_markers.append(marker)
            errors = self.apply_leave_page.get_error_messages()
            assert not errors, f"Apply leave failed with validation errors: {errors}"

        with allure.step("Verify leave status is Pending"):
            self.apply_leave_page.navigate_to_my_leave()

            row_text = self.my_leave_page.get_row_by_marker(marker)
            assert row_text is not None, f"Could not find request with marker '{marker}' in My Leave"
            assert "pending" in row_text.lower(), f"Expected Pending status, got: {row_text}"

    @pytest.mark.apply_leave_past_date
    @allure.story("TC03 - Apply leave with a past date")
    def test_apply_leave_past_date_shows_error(self, leave_data, ensure_leave_entitlement):
        with allure.step("Navigate to Apply Leave"):
            self._navigate_to_apply_leave()

        with allure.step("Apply leave with a past date"):
            self.apply_leave_page.apply_leave(**leave_data["past_date_leave"])

        with allure.step("Verify error message is shown"):
            errors = self.apply_leave_page.get_error_messages()
            assert any(
                "should be after" in e.lower() or "invalid" in e.lower()
                for e in errors
            ), f"Expected date error not found, got: {errors}"

    @pytest.mark.apply_leave_missing_field
    @allure.story("TC04 - Apply leave with a missing field")
    def test_apply_leave_missing_field_shows_error(self, leave_data):
        with allure.step("Navigate to Apply Leave"):
            self._navigate_to_apply_leave()

        with allure.step("Submit leave with missing required field"):
            self.apply_leave_page.apply_leave(**leave_data["missing_field_leave"])

        with allure.step("Verify required field error is shown"):
            assert len(self.apply_leave_page.get_error_messages()) > 0


@pytest.mark.leave
@pytest.mark.regression
@allure.epic("Leave Management")
@allure.feature("Approve/Reject Leave")
class TestManageLeave:

    # --- Fixtures and navigation helpers ---

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.driver = driver
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeaveListPage(driver)
        self.leave_list_page = LeaveListPage(driver)
        self.my_leave_page = MyLeavePage(driver)

    def _go_to_leave_list(self):
        self.dashboard_page.navigate_to_leave_page()
        self.leave_page.navigate_to_leave_list()
        assert self.leave_list_page.is_page_displayed()

    # --- Approval and rejection tests ---

    @pytest.mark.approve_leave
    @allure.story("TC05 - Admin approve leave")
    @allure.description(
        "Create a dynamic employee, grant entitlement, assign leave, then approve it as Admin."
    )
    def test_admin_approve_leave(self, pending_leave):
        marker = pending_leave["marker"]

        with allure.step("Navigate to Leave List"):
            self._go_to_leave_list()
            self.leave_list_page.search_pending_leave_for_employee(
                pending_leave["employee_name"]
            )

        with allure.step("Approve the pending leave request"):
            self.leave_list_page.approve_leave_by_marker(marker)

        with allure.step("Verify Scheduled status in employee My Leave"):
            self._verify_employee_status(pending_leave, "scheduled")

    @pytest.mark.reject_leave
    @allure.story("TC06 - Admin reject leave")
    def test_admin_reject_leave(self, pending_leave):
        marker = pending_leave["marker"]

        with allure.step("Navigate to Leave List"):
            self._go_to_leave_list()
            self.leave_list_page.search_pending_leave_for_employee(
                pending_leave["employee_name"]
            )

        with allure.step("Reject the pending leave request"):
            self.leave_list_page.reject_leave_by_marker(marker)

        with allure.step("Verify Rejected status in employee My Leave"):
            self._verify_employee_status(pending_leave, "rejected")

    def _verify_employee_status(self, pending_leave, expected_status):
        employee_login = LoginPage(self.driver)
        employee_login.logout()
        employee_login.login(
            pending_leave["employee_username"], ConfigReader.get_test_user_password()
        )
        employee_dashboard = DashboardPage(self.driver)
        employee_dashboard.navigate_to_leave_page()
        employee_leave = LeaveListPage(self.driver)
        employee_leave.navigate_to_my_leave()
        row_text = self.my_leave_page.wait_for_status_by_marker(
            pending_leave["marker"], expected_status
        )
        assert expected_status in row_text.lower(), (
            f"Expected employee status '{expected_status}', got: {row_text}"
        )


@pytest.mark.leave
@pytest.mark.regression
@allure.epic("Leave Management")
@allure.feature("View Leave")
class TestViewLeave:

    # --- Fixtures ---

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeaveListPage(driver)
        self.my_leave_page = MyLeavePage(driver)

    # --- Verification tests ---

    @pytest.mark.view_my_leave
    @allure.story("TC07 - View the personal leave list")
    def test_view_own_leave_list(self):
        with allure.step("Navigate to My Leave"):
            self.dashboard_page.navigate_to_leave_page()
            self.leave_page.navigate_to_my_leave()

        with allure.step("Verify leave list is displayed"):
            assert self.my_leave_page.is_leave_list_visible()

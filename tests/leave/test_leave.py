import allure
import pytest
from utils.test_data import TestData
from pages.dashboard_page import DashboardPage
from pages.leave.leave_page import LeavePage
from pages.leave.leave_types_page import LeaveTypesPage
from pages.leave.apply_leave_page import ApplyLeavePage
from pages.leave.my_leave_page import MyLeavePage
from pages.leave.leave_list_page import LeaveListPage
from pages.login_page import LoginPage


@pytest.mark.leave
class TestEmployeeManagement:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.driver = driver
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeavePage(driver)
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

@pytest.mark.leave
@allure.epic("Leave Management")
@allure.feature("Apply Leave")
class TestApplyLeave:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeavePage(driver)
        self.apply_leave_page = ApplyLeavePage(driver)
        self.my_leave_page = MyLeavePage(driver)

    def _navigate_to_apply_leave(self):
        self.dashboard_page.navigate_to_leave_page()
        assert self.leave_page.is_leave_page_displayed()
        self.leave_page.navigate_to_apply_leave()
        assert self.apply_leave_page.is_page_displayed()

    @pytest.mark.apply_leave_valid
    @allure.story("TC02 - Apply leave hợp lệ")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_apply_valid_leave_status_pending(self, leave_data, ensure_leave_entitlement):
        with allure.step("Navigate to Apply Leave"):
            self._navigate_to_apply_leave()

        marker = TestData.generate_unique_marker()
        leave_type = leave_data["valid_leave"]["leave_type"]

        with allure.step("Apply a valid leave request"):
            # Dùng ngày sinh động qua date_generator (thay vì ngày cố định trong
            # leave_data) và tự động thử lại nếu trùng với leave request cũ
            # còn leftover từ lần chạy trước ('Overlapping Leave Request').
            self.apply_leave_page.apply_leave_avoiding_overlap(
                leave_type=leave_type,
                date_generator=TestData.generate_future_leave_dates,
                comment=marker,
            )
            errors = self.apply_leave_page.get_error_messages()
            assert not errors, f"Apply leave failed with validation errors: {errors}"

        with allure.step("Verify leave status is Pending"):
            self.apply_leave_page.navigate_to_my_leave()

            row_text = self.my_leave_page.get_row_by_marker(marker)
            assert row_text is not None, f"Không tìm thấy request với marker '{marker}' trong My Leave"
            assert "pending" in row_text.lower(), f"Expected Pending status, got: {row_text}"

    @allure.story("TC03 - Apply leave ngày quá khứ")
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

    @allure.story("TC04 - Apply leave thiếu field")
    def test_apply_leave_missing_field_shows_error(self, leave_data):
        with allure.step("Navigate to Apply Leave"):
            self._navigate_to_apply_leave()

        with allure.step("Submit leave with missing required field"):
            self.apply_leave_page.apply_leave(**leave_data["missing_field_leave"])

        with allure.step("Verify required field error is shown"):
            assert len(self.apply_leave_page.get_error_messages()) > 0


@pytest.mark.leave
@allure.epic("Leave Management")
@allure.feature("Approve/Reject Leave")
class TestManageLeave:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.driver = driver
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeavePage(driver)
        self.leave_list_page = LeaveListPage(driver)
        self.my_leave_page = MyLeavePage(driver)

    def _go_to_leave_list(self):
        self.dashboard_page.navigate_to_leave_page()
        self.leave_page.navigate_to_leave_list()
        assert self.leave_list_page.is_page_displayed()

    @allure.story("TC05 - Admin approve leave")
    @allure.description(
        "Tạo employee động, cấp entitlement, assign leave rồi để Admin approve."
    )
    def test_admin_approve_leave(self, pending_leave):
        marker = pending_leave["marker"]

        with allure.step("Navigate to Leave List"):
            self._go_to_leave_list()
            self.leave_list_page.search_scheduled_leave_for_employee(
                pending_leave["employee_name"]
            )

        with allure.step("Approve the pending leave request"):
            self.leave_list_page.approve_leave_by_marker(marker)

        with allure.step("Verify Scheduled status in employee My Leave"):
            self._verify_employee_status(pending_leave, "scheduled")

    @allure.story("TC06 - Admin reject leave")
    def test_admin_reject_leave(self, pending_leave):
        marker = pending_leave["marker"]

        with allure.step("Navigate to Leave List"):
            self._go_to_leave_list()
            self.leave_list_page.search_scheduled_leave_for_employee(
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
            pending_leave["employee_username"], TestData.DEFAULT_PASSWORD
        )
        employee_dashboard = DashboardPage(self.driver)
        employee_dashboard.navigate_to_leave_page()
        employee_leave = LeavePage(self.driver)
        employee_leave.navigate_to_my_leave()
        row_text = self.my_leave_page.get_row_by_marker(pending_leave["marker"])
        assert row_text is not None, "Không tìm thấy request trong My Leave của employee"
        assert expected_status in row_text.lower(), (
            f"Expected employee status '{expected_status}', got: {row_text}"
        )


@pytest.mark.leave
@allure.epic("Leave Management")
@allure.feature("View Leave")
class TestViewLeave:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.leave_page = LeavePage(driver)
        self.my_leave_page = MyLeavePage(driver)

    @allure.story("TC07 - Xem leave list của bản thân")
    def test_view_own_leave_list(self):
        with allure.step("Navigate to My Leave"):
            self.dashboard_page.navigate_to_leave_page()
            self.leave_page.navigate_to_my_leave()

        with allure.step("Verify leave list is displayed"):
            assert self.my_leave_page.is_leave_list_visible()

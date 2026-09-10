import logging

import pytest

from pages.admin.user_management_page import UserManagementPage
from pages.dashboard_page import DashboardPage
from pages.leave.add_entitlements_page import AddEntitlementPage
from pages.leave.add_user_page import LeaveAddUserPage
from pages.leave.apply_leave_page import ApplyLeavePage
from pages.leave.leave_page import LeavePage
from pages.leave.my_leave_page import MyLeavePage
from pages.login_page import LoginPage
from pages.pim.create_employee_page import CreateEmployee
from pages.pim.pim_page import PIMPage
from utils.config_reader import ConfigReader
from utils.test_data import TestData

logger = logging.getLogger(__name__)


@pytest.fixture
def leave_data():
    valid_leave = ConfigReader.get_leave_data("valid_leave")
    from_date, to_date = TestData.generate_future_leave_dates()
    past_leave = ConfigReader.get_leave_data("past_date_leave")
    past_from, past_to = TestData.generate_past_leave_dates()

    return {
        "employee_name": ConfigReader.get_leave_employee_name(),
        "entitlement_days_to_grant": ConfigReader.get_leave_data(
            "entitlement_days_to_grant"
        ),
        "valid_leave": {**valid_leave, "from_date": from_date, "to_date": to_date},
        "past_date_leave": {
            **past_leave,
            "from_date": past_from,
            "to_date": past_to,
        },
        "missing_field_leave": ConfigReader.get_leave_data("missing_field_leave"),
    }


@pytest.fixture
def ensure_leave_entitlement(driver, login, leave_data):
    dashboard_page = DashboardPage(driver)
    leave_page = LeavePage(driver)
    apply_leave_page = ApplyLeavePage(driver)
    desired_leave_type = leave_data["valid_leave"]["leave_type"]
    days_to_grant = leave_data.get("entitlement_days_to_grant", 30)

    dashboard_page.navigate_to_leave_page()
    assert leave_page.is_leave_page_displayed(), "Leave page is not displayed"
    leave_page.navigate_to_apply_leave()
    assert apply_leave_page.is_page_displayed(), "Apply Leave page is not displayed"

    if apply_leave_page.has_no_leave_balance():
        already_exists = False
    else:
        already_exists = apply_leave_page.has_leave_type_option(desired_leave_type)

    if already_exists:
        current_balance = apply_leave_page.get_current_balance(desired_leave_type)
        already_exists = current_balance >= 3
        logger.info("Leave type '%s' balance: %s", desired_leave_type, current_balance)

    if not already_exists:
        apply_leave_page.navigate_to_add_entitlement()
        entitlement_page = AddEntitlementPage(driver)
        assert entitlement_page.is_page_displayed()
        entitlement_page.add_entitlement(
            leave_type=desired_leave_type,
            days=str(days_to_grant),
        )
        assert entitlement_page.is_success(), "Add entitlement failed"


def _cleanup_pending_leave(driver, employee_username, employee_name, marker):
    cleanup_errors = []

    if employee_username and marker:
        try:
            login_page = LoginPage(driver)
            login_page.logout()
            login_page.login_and_wait(
                employee_username,
                ConfigReader.get_test_user_password(),
                DashboardPage(driver).leave_btn,
            )
            employee_dashboard = DashboardPage(driver)
            employee_dashboard.navigate_to_leave_page()
            employee_leave_page = LeavePage(driver)
            employee_leave_page.navigate_to_my_leave()
            employee_my_leave_page = MyLeavePage(driver)
            if employee_my_leave_page.get_row_by_marker(marker) is not None:
                employee_my_leave_page.cancel_leave_by_marker(marker)
        except Exception as error:
            logger.warning("Could not cancel leave request '%s': %s", marker, error)

    if employee_name:
        try:
            login_page = LoginPage(driver)
            login_page.logout()
            admin_user = ConfigReader.get_user("admin")
            login_page.login(admin_user["username"], admin_user["password"])

            dashboard_page = DashboardPage(driver)
            dashboard_page.navigate_to_admin_page()
            user_management_page = UserManagementPage(driver)
            if employee_username:
                user_management_page.enter_username_search(employee_username)
                user_management_page.click_search_btn()
                if user_management_page.is_user_displayed(employee_username):
                    user_management_page.delete_user_row(employee_username)
                    user_management_page.confirm_delete()
                    user_management_page.wait_for_loading_to_disappear()

            dashboard_page.navigate_to_pim_page()
            pim_page = PIMPage(driver)
            pim_page.search_by_employee_name(employee_name)
            if not pim_page.is_no_records_found_displayed():
                pim_page.delete_first_row_via_icon()
                pim_page.confirm_delete()
                pim_page.wait_for_loading_to_disappear()
        except Exception as error:
            cleanup_errors.append(error)

    if cleanup_errors:
        raise AssertionError(
            f"Failed to clean up leave test resources for '{employee_username}'"
        ) from cleanup_errors[0]


def _create_leave_employee(driver):
    dashboard_page = DashboardPage(driver)
    dashboard_page.navigate_to_pim_page()

    pim_page = PIMPage(driver)
    create_employee_page = CreateEmployee(driver)
    pim_page.navigate_to_add_employee()

    first_name = TestData.generate_employee_name("Leave")
    last_name = TestData.generate_employee_name("Employee")
    create_employee_page.create_employee(first_name, last_name)
    return f"{first_name} {last_name}"


def _create_leave_user(driver, employee_name):
    dashboard_page = DashboardPage(driver)
    dashboard_page.navigate_to_admin_page()

    user_management_page = UserManagementPage(driver)
    user_management_page.navigate_to_add_user()
    add_user_page = LeaveAddUserPage(driver)
    employee_username = TestData.generate_username("leave_employee")
    employee_password = ConfigReader.get_test_user_password()
    add_user_page.create_user_for_employee(
        role=TestData.DEFAULT_ROLE,
        status=TestData.DEFAULT_STATUS,
        username=employee_username,
        password=employee_password,
        employee_name=employee_name,
    )
    assert add_user_page.is_save_successful(), (
        f"Could not create ESS user '{employee_username}' for '{employee_name}'"
    )
    return employee_username, employee_password


def _create_pending_leave_request(driver, leave_data, employee_name, username, password):
    dashboard_page = DashboardPage(driver)
    leave_page = LeavePage(driver)

    dashboard_page.navigate_to_leave_page()
    assert leave_page.is_leave_page_displayed(), (
        "Leave page did not finish loading after creating the ESS user"
    )
    leave_page.wait_for_loading_to_disappear()
    leave_page.navigate_to_add_entitlement()
    entitlement_page = AddEntitlementPage(driver)
    assert entitlement_page.is_page_displayed()
    entitlement_page.add_entitlement(
        leave_type=leave_data["valid_leave"]["leave_type"],
        days=str(leave_data["entitlement_days_to_grant"]),
        employee_name=employee_name,
    )
    assert entitlement_page.is_success(), "Could not add entitlement"

    marker = TestData.generate_unique_marker()
    leave_type = leave_data["valid_leave"]["leave_type"]
    from_date, to_date = TestData.generate_future_leave_dates()

    login_page = LoginPage(driver)
    login_page.logout()
    login_page.login_and_wait(
        username,
        password,
        DashboardPage(driver).leave_btn,
    )
    employee_dashboard = DashboardPage(driver)
    employee_dashboard.navigate_to_leave_page()
    employee_leave_page = LeavePage(driver)
    employee_leave_page.navigate_to_apply_leave()
    employee_apply_page = ApplyLeavePage(driver)
    assert employee_apply_page.is_page_displayed()
    employee_apply_page.apply_leave(
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        comment=marker,
        wait_for_feedback=False,
    )
    errors = employee_apply_page.get_error_messages()
    assert not errors, f"Could not create pending leave: {errors}"
    employee_apply_page.navigate_to_my_leave()
    assert MyLeavePage(driver).get_row_by_marker(marker) is not None, (
        f"Leave request '{marker}' was not created for '{employee_name}'"
    )

    login_page.logout()
    admin_user = ConfigReader.get_user("admin")
    LoginPage(driver).login(admin_user["username"], admin_user["password"])

    return {
        "from_date": from_date,
        "to_date": to_date,
        "marker": marker,
    }


@pytest.fixture
def pending_leave(request, driver, login, leave_data):
    employee_username = None
    employee_name = None
    marker = None

    request.addfinalizer(
        lambda: _cleanup_pending_leave(
            driver, employee_username, employee_name, marker
        )
    )

    employee_name = _create_leave_employee(driver)
    employee_username, employee_password = _create_leave_user(
        driver, employee_name
    )
    pending_request = _create_pending_leave_request(
        driver,
        leave_data,
        employee_name,
        employee_username,
        employee_password,
    )

    yield {
        **leave_data["valid_leave"],
        **pending_request,
        "employee_name": employee_name,
        "employee_username": employee_username,
    }
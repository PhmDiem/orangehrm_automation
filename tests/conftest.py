import logging

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from pages.admin.user_management_page import UserManagementPage
from pages.dashboard_page import DashboardPage
from pages.leave.add_entitlements_page import AddEntitlementPage
from pages.leave.add_user_page import LeaveAddUserPage
from pages.leave.apply_leave_page import ApplyLeavePage
from pages.leave.leave_page import LeavePage
from pages.leave.my_leave_page import MyLeavePage
from pages.pim.create_employee_page import CreateEmployee
from pages.pim.pim_page import PIMPage
from pages.login_page import LoginPage
from utils.allure_helper import attach_failure_screenshot
from utils.browser_options import build_chrome_options
from utils.chromedriver import get_chromedriver_path
from utils.config_reader import ConfigReader
from utils.test_data import TestData

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def driver():
    options, temp_profile = build_chrome_options()
    driver = None

    try:
        browser = ConfigReader.get_browser().strip().lower()

        if browser == "chrome":
            driver = webdriver.Chrome(
                service=Service(get_chromedriver_path()),
                options=options,
            )
        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                "Currently supported browsers: chrome"
            )

        driver.implicitly_wait(ConfigReader.get_implicit_wait())
        driver.set_page_load_timeout(ConfigReader.get_explicit_wait())

        if not ConfigReader.is_headless():
            driver.maximize_window()

        driver.get(ConfigReader.get_url())
        yield driver
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        temp_profile.cleanup()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver:
        attach_failure_screenshot(driver, item.name)


@pytest.fixture
def login(driver):
    user = ConfigReader.get_user("admin")
    login_page = LoginPage(driver)
    login_page.login(user["username"], user["password"])
    return login_page


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

    yield


@pytest.fixture
def pending_leave(driver, login, leave_data):
    dashboard_page = DashboardPage(driver)
    leave_page = LeavePage(driver)

    dashboard_page.navigate_to_pim_page()
    pim_page = PIMPage(driver)
    create_employee_page = CreateEmployee(driver)
    pim_page.navigate_to_add_employee()
    first_name = TestData.generate_employee_name("Leave")
    last_name = TestData.generate_employee_name("Employee")
    create_employee_page.create_employee(first_name, last_name)
    employee_name = f"{first_name} {last_name}"

    dashboard_page.navigate_to_admin_page()
    user_management_page = UserManagementPage(driver)
    user_management_page.navigate_to_add_user()
    add_user_page = LeaveAddUserPage(driver)
    employee_username = TestData.generate_username("leave_employee")
    employee_password = TestData.DEFAULT_PASSWORD
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

    dashboard_page.navigate_to_leave_page()
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
        employee_username,
        employee_password,
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

    yield {
        **leave_data["valid_leave"],
        "from_date": from_date,
        "to_date": to_date,
        "marker": marker,
        "employee_name": employee_name,
        "employee_username": employee_username,
    }

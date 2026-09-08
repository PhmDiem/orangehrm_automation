import logging
import pytest
from selenium import webdriver
from pages.leave.leave_page import LeavePage
from pages.leave.add_entitlements_page import AddEntitlementPage

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.leave.apply_leave_page import ApplyLeavePage
from pages.pim.pim_page import PIMPage
from pages.pim.create_employee_page import CreateEmployee
from pages.admin.user_management_page import UserManagementPage
from pages.admin.add_user_page import AddUserPage
from utils.allure_helper import attach_failure_screenshot
from utils.browser_options import build_chrome_options
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
            driver = webdriver.Chrome(options=options)
        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                "Currently supported browsers: chrome"
            )

        driver.implicitly_wait(
            ConfigReader.get_implicit_wait()
        )

        driver.set_page_load_timeout(
            ConfigReader.get_explicit_wait()
        )

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
        attach_failure_screenshot(
            driver,
            item.name,
        )


@pytest.fixture
def login(driver):
    user = ConfigReader.get_user("admin")

    login_page = LoginPage(driver)

    login_page.login(
        user["username"],
        user["password"],
    )

    return login_page

@pytest.fixture
def leave_data():
    """Kết hợp leave_type tĩnh (từ JSON) với ngày tháng sinh động
    (từ TestData) để tránh test bị fail do ngày hết hạn theo thời gian."""

    valid_leave = ConfigReader.get_leave_data("valid_leave")
    from_date, to_date = TestData.generate_future_leave_dates()
    valid_leave = {**valid_leave, "from_date": from_date, "to_date": to_date}

    past_date_leave = ConfigReader.get_leave_data("past_date_leave")
    past_from, past_to = TestData.generate_past_leave_dates()
    past_date_leave = {**past_date_leave, "from_date": past_from, "to_date": past_to}

    return {
        "employee_name": ConfigReader.get_leave_employee_name(),
        "entitlement_days_to_grant": ConfigReader.get_leave_data(
            "entitlement_days_to_grant"
        ),
        "valid_leave": valid_leave,
        "past_date_leave": past_date_leave,
        "missing_field_leave": ConfigReader.get_leave_data("missing_field_leave"),
    }


@pytest.fixture
def ensure_leave_entitlement(driver, login, leave_data):
    """
    Đảm bảo leave type mong muốn có balance đủ cho một request tối thiểu.

    a. Trang báo 'No Leave Types with Leave Balance' -> chưa có gì cả -> cấp.
    b. Có leave type khác nhưng KHÔNG có đúng loại cần -> cấp.
    c. Đã có đúng loại nhưng balance bằng 0/không đủ -> cập nhật entitlement.
    """
    dashboard_page = DashboardPage(driver)
    leave_page = LeavePage(driver)
    apply_leave_page = ApplyLeavePage(driver)

    desired_leave_type = leave_data["valid_leave"]["leave_type"]
    days_to_grant = leave_data.get("entitlement_days_to_grant", 30)

    dashboard_page.navigate_to_leave_page()
    assert leave_page.is_leave_page_displayed(), "Leave page is not displayed"

    leave_page.navigate_to_apply_leave()
    assert apply_leave_page.is_page_displayed(), "Apply Leave page is not displayed"

    # Check trước khi đụng vào dropdown - tránh timeout khi dropdown
    # không tồn tại/rỗng do chưa có bất kỳ entitlement nào
    if apply_leave_page.has_no_leave_balance():
        already_exists = False
        logger.info("Trang báo 'No Leave Types with Leave Balance' -> chưa có entitlement nào.")
    else:
        already_exists = apply_leave_page.has_leave_type_option(desired_leave_type)

    current_balance = 0.0
    if already_exists:
        # A leave type can remain in the dropdown after its balance reaches 0.
        # Treat that state as missing so Apply Leave is tested with a usable
        # entitlement instead of silently submitting an empty form.
        current_balance = apply_leave_page.get_current_balance(desired_leave_type)
        already_exists = current_balance >= 3
        logger.info(
            "Leave type '%s' balance hiện tại: %s; đủ dùng=%s.",
            desired_leave_type,
            current_balance,
            already_exists,
        )

    if already_exists:
        logger.info("Leave type '%s' đã có balance đủ dùng, bỏ qua bước cấp entitlement.", desired_leave_type)
    else:
        logger.info("Leave type '%s' chưa tồn tại -> tiến hành cấp %s ngày.", desired_leave_type, days_to_grant)
        apply_leave_page.navigate_to_add_entitlement()

        entitlement_page = AddEntitlementPage(driver)
        assert entitlement_page.is_page_displayed()

        entitlement_page.add_entitlement(
            leave_type=desired_leave_type,
            days=str(days_to_grant),
        )
        assert entitlement_page.is_success(), "Add entitlement thất bại"

    yield

@pytest.fixture
def pending_leave(driver, login, leave_data):
    """Create a Scheduled request by logging in as a fresh employee."""
    dashboard_page = DashboardPage(driver)
    leave_page = LeavePage(driver)
    admin_login_page = login

    # Create a target employee dynamically so reset/demo seed data cannot break
    # the approval flow.
    dashboard_page.navigate_to_pim_page()
    pim_page = PIMPage(driver)
    create_employee_page = CreateEmployee(driver)
    pim_page.navigate_to_add_employee()
    first_name = TestData.generate_employee_name("Leave")
    last_name = TestData.generate_employee_name("Employee")
    create_employee_page.create_employee(first_name, last_name)
    employee_name = f"{first_name} {last_name}"

    # The employee needs an ESS account to create a real employee-owned leave
    # request. Admin-only Assign Leave does not expose the same workflow.
    dashboard_page.navigate_to_admin_page()
    user_management_page = UserManagementPage(driver)
    user_management_page.navigate_to_add_user()
    add_user_page = AddUserPage(driver)
    employee_username = TestData.generate_username("leave_employee")
    employee_password = TestData.DEFAULT_PASSWORD
    add_user_page.create_user(
        role=TestData.DEFAULT_ROLE,
        status=TestData.DEFAULT_STATUS,
        username=employee_username,
        password=employee_password,
        employee_name=employee_name,
    )
    assert add_user_page.is_save_successful(), (
        f"Không tạo được user ESS '{employee_username}' cho employee '{employee_name}'"
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
    assert entitlement_page.is_success(), "Không cấp được entitlement cho employee test"

    marker = TestData.generate_unique_marker()
    leave_type = leave_data["valid_leave"]["leave_type"]
    from_date, to_date = TestData.generate_future_leave_dates()

    # Switch from Admin to the employee account before applying.
    admin_login_page.logout()
    employee_login_page = LoginPage(driver)
    employee_login_page.login_and_wait(
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
    )

    errors = employee_apply_page.get_error_messages()
    assert not errors, f"Không tạo được leave pending cho test approve/reject: {errors}"

    # Return to Admin for Leave List approval/rejection.
    employee_login_page.logout()
    admin_login_page = LoginPage(driver)
    admin_user = ConfigReader.get_user("admin")
    admin_login_page.login(admin_user["username"], admin_user["password"])

    yield {
        **leave_data["valid_leave"],
        "from_date": from_date,
        "to_date": to_date,
        "marker": marker,
        "employee_name": employee_name,
        "employee_username": employee_username,
    }

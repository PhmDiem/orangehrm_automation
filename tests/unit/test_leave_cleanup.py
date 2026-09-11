from types import SimpleNamespace

from tests.leave import conftest as leave_conftest


class FakeLoginPage:
    events = []

    def __init__(self, driver):
        self.driver = driver

    def logout(self):
        self.events.append("logout")

    def login_and_wait(self, username, password, dashboard_locator):
        self.events.append(("login", username, password, dashboard_locator))

    def login(self, username, password):
        self.events.append(("login_admin", username, password))


class FakeDashboardPage:
    leave_btn = "leave"

    def __init__(self, driver):
        self.driver = driver

    def navigate_to_leave_page(self):
        FakeLoginPage.events.append("navigate_leave")

    def navigate_to_admin_page(self):
        FakeLoginPage.events.append("navigate_admin")

    def navigate_to_pim_page(self):
        FakeLoginPage.events.append("navigate_pim")


class FakeLeavePage:
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_my_leave(self):
        FakeLoginPage.events.append("navigate_my_leave")


class FakeMyLeavePage:
    def __init__(self, driver):
        self.driver = driver

    def get_row_by_marker(self, marker):
        return {"marker": marker}

    def cancel_leave_by_marker(self, marker):
        FakeLoginPage.events.append(("cancel", marker))


class FakeUserManagementPage:
    def __init__(self, driver):
        self.driver = driver

    def enter_username_search(self, username):
        FakeLoginPage.events.append(("search_user", username))

    def click_search_btn(self):
        FakeLoginPage.events.append("search_user_submit")

    def is_user_displayed(self, username):
        return True

    def delete_user_row(self, username):
        FakeLoginPage.events.append(("delete_user", username))

    def confirm_delete(self):
        FakeLoginPage.events.append("confirm_user_delete")

    def wait_for_loading_to_disappear(self):
        FakeLoginPage.events.append("wait")


class FakePIMPage:
    def __init__(self, driver):
        self.driver = driver

    def search_by_employee_name(self, employee_name):
        FakeLoginPage.events.append(("search_employee", employee_name))

    def is_no_records_found_displayed(self):
        return False

    def delete_first_row_via_icon(self):
        FakeLoginPage.events.append("delete_employee")

    def confirm_delete(self):
        FakeLoginPage.events.append("confirm_employee_delete")

    def wait_for_loading_to_disappear(self):
        FakeLoginPage.events.append("wait")


def test_cleanup_pending_leave_cancels_request_and_removes_resources(monkeypatch):
    FakeLoginPage.events = []
    monkeypatch.setattr(leave_conftest, "LoginPage", FakeLoginPage)
    monkeypatch.setattr(leave_conftest, "DashboardPage", FakeDashboardPage)
    monkeypatch.setattr(leave_conftest, "LeaveListPage", FakeLeavePage)
    monkeypatch.setattr(leave_conftest, "MyLeavePage", FakeMyLeavePage)
    monkeypatch.setattr(
        leave_conftest,
        "UserManagementPage",
        FakeUserManagementPage,
    )
    monkeypatch.setattr(leave_conftest, "PIMPage", FakePIMPage)
    monkeypatch.setattr(
        leave_conftest.ConfigReader,
        "get_test_user_password",
        staticmethod(lambda: "test-password"),
    )
    monkeypatch.setattr(
        leave_conftest.ConfigReader,
        "get_user",
        staticmethod(lambda user_type: {"username": "Admin", "password": "admin123"}),
    )

    leave_conftest._cleanup_pending_leave(
        SimpleNamespace(),
        employee_username="leave_user",
        employee_name="Leave Employee",
        marker="AUTOTEST_1",
    )

    assert ("cancel", "AUTOTEST_1") in FakeLoginPage.events
    assert ("delete_user", "leave_user") in FakeLoginPage.events
    assert ("search_employee", "Leave Employee") in FakeLoginPage.events
    assert "delete_employee" in FakeLoginPage.events

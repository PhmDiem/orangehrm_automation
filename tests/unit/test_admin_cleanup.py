import pytest

from tests.admin.test_admin import TestUserManagement as AdminTestCase


pytestmark = pytest.mark.regression


class FakeRequest:
    def __init__(self):
        self.finalizer = None

    def addfinalizer(self, finalizer):
        self.finalizer = finalizer


class FakeDashboardPage:
    def __init__(self, events):
        self.events = events

    def navigate_to_admin_page(self):
        self.events.append("navigate_admin")


class FakeUserManagementPage:
    def __init__(self, events):
        self.events = events

    def is_user_displayed(self, username):
        return True

    def delete_user_row(self, username):
        self.events.append(("delete_user", username))

    def confirm_delete(self):
        self.events.append("confirm_delete")


def test_created_users_fixture_cleanup_deletes_created_users():
    events = []
    request = FakeRequest()
    test_instance = AdminTestCase.__new__(AdminTestCase)
    test_instance.dashboard_page = FakeDashboardPage(events)
    test_instance.user_management_page = FakeUserManagementPage(events)
    test_instance._navigate_to_admin = lambda: events.append("navigate_admin_helper")
    test_instance._search_user_by_username = (
        lambda username: events.append(("search_user", username))
    )

    usernames = AdminTestCase.created_users.__wrapped__(
        test_instance, request
    )
    usernames.append("created_user")
    request.finalizer()

    assert "navigate_admin_helper" in events
    assert ("search_user", "created_user") in events
    assert ("delete_user", "created_user") in events
    assert "confirm_delete" in events

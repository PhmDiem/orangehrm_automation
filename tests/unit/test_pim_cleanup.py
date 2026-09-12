import pytest

from tests.pim.test_pim import TestEmployeeManagement as PimTestCase


pytestmark = pytest.mark.regression


class FakeDashboardPage:
    def __init__(self, events):
        self.events = events

    def navigate_to_pim_page(self):
        self.events.append("navigate_pim")


class FakePIMPage:
    def __init__(self, events):
        self.events = events

    def search_by_employee_name(self, employee_name):
        self.events.append(("search_employee", employee_name))

    def is_no_records_found_displayed(self):
        return False

    def delete_first_row_with_bulk_action(self):
        self.events.append("delete_employee")

    def confirm_delete(self):
        self.events.append("confirm_delete")

    def wait_for_loading_to_disappear(self):
        self.events.append("wait")


def test_cleanup_created_employees_deletes_created_employees():
    events = []
    test_instance = PimTestCase.__new__(PimTestCase)
    test_instance._created_employees = [("Test", "Employee")]
    test_instance.dashboard_page = FakeDashboardPage(events)
    test_instance.pim_page = FakePIMPage(events)
    test_instance._navigate_to_pim = lambda: events.append("navigate_pim_helper")
    test_instance._search_employee_by_name = (
        lambda first_name, last_name: events.append(
            ("search_helper", first_name, last_name)
        )
    )

    test_instance._cleanup_created_employees()

    assert "navigate_pim_helper" in events
    assert ("search_helper", "Test", "Employee") in events
    assert "delete_employee" in events
    assert "confirm_delete" in events
    assert "wait" in events

import pytest

from tests.my_info.test_my_info import TestMyInfo as MyInfoTestCase


pytestmark = pytest.mark.regression


class FakeDashboardPage:
    def __init__(self, events):
        self.events = events

    def navigate_to_my_info_page(self):
        self.events.append("navigate_my_info")


class FakePersonalDetailsPage:
    def __init__(self, events):
        self.events = events

    def open_personal_details(self):
        self.events.append("open_personal_details")

    def enter_nickname_if_available(self, value):
        self.events.append(("restore_nickname", value))

    def select_gender(self, value):
        self.events.append(("restore_gender", value))

    def select_blood_type_if_available(self, value):
        self.events.append(("restore_blood_type", value))

    def save(self):
        self.events.append("save_personal_details")

    def is_saved(self):
        self.events.append("verify_personal_details")


class FakeContactDetailsPage:
    def __init__(self, events):
        self.events = events

    def open_contact_details(self):
        self.events.append("open_contact_details")

    def enter_street_1(self, value):
        self.events.append(("restore_street", value))

    def enter_city(self, value):
        self.events.append(("restore_city", value))

    def enter_mobile(self, value):
        self.events.append(("restore_mobile", value))

    def save(self):
        self.events.append("save_contact_details")

    def is_saved(self):
        self.events.append("verify_contact_details")


class FakeEmergencyContactsPage:
    def __init__(self, events):
        self.events = events

    def open_emergency_contacts(self):
        self.events.append("open_emergency_contacts")

    def get_emergency_rows_text(self):
        return ["Emergency Contact"]

    def delete_emergency_contact(self, name):
        self.events.append(("delete_emergency_contact", name))


def test_restore_my_info_restores_snapshots_and_deletes_created_contacts():
    events = []
    test_instance = MyInfoTestCase.__new__(MyInfoTestCase)
    test_instance._my_info_changed = True
    test_instance._personal_snapshot = {
        "nickname": "Original Nickname",
        "gender": "Female",
        "blood_type": "O+",
    }
    test_instance._contact_snapshot = {
        "street_1": "Original Street",
        "city": "Original City",
        "mobile": "123456789",
    }
    test_instance._created_emergency_contacts = ["Emergency Contact"]
    test_instance.dashboard_page = FakeDashboardPage(events)
    test_instance.personal_details_page = FakePersonalDetailsPage(events)
    test_instance.contact_details_page = FakeContactDetailsPage(events)
    test_instance.emergency_contacts_page = FakeEmergencyContactsPage(events)

    test_instance._restore_my_info()

    assert "navigate_my_info" in events
    assert ("restore_nickname", "Original Nickname") in events
    assert ("restore_gender", "Female") in events
    assert ("restore_blood_type", "O+") in events
    assert ("restore_street", "Original Street") in events
    assert ("restore_city", "Original City") in events
    assert ("restore_mobile", "123456789") in events
    assert ("delete_emergency_contact", "Emergency Contact") in events


def test_restore_my_info_skips_work_when_no_changes_were_made():
    test_instance = MyInfoTestCase.__new__(MyInfoTestCase)
    test_instance._my_info_changed = False

    test_instance._restore_my_info()

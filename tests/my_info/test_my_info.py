import allure
import pytest
import logging

from pages.dashboard_page import DashboardPage
from pages.my_info.personal_details_page import PersonalDetailsPage
from pages.my_info.contact_details_page import ContactDetailsPage
from pages.my_info.emergency_contacts_page import EmergencyContactsPage
from utils.config_reader import ConfigReader
from utils.test_data import TestData

logger = logging.getLogger(__name__)

@pytest.mark.my_info
@pytest.mark.regression
class TestMyInfo:

    # --- Fixtures and setup ---

    @pytest.fixture(autouse=True)
    def setup(self, driver, login, request):
        self._created_emergency_contacts = []
        self._my_info_changed = False
        self.dashboard_page = DashboardPage(driver)
        self.personal_details_page = PersonalDetailsPage(driver)
        self.contact_details_page = ContactDetailsPage(driver)
        self.emergency_contacts_page = EmergencyContactsPage(driver)

        self.dashboard_page.navigate_to_my_info_page()
        assert self.personal_details_page.open(), "My Info page is not displayed"
        self._personal_snapshot = self._capture_personal_details()
        self._contact_snapshot = self._capture_contact_details()
        self.personal_details_page.open_personal_details()
        request.addfinalizer(self._restore_my_info)

    # --- Snapshot and cleanup helpers ---

    def _capture_personal_details(self):
        nickname = None
        blood_type = None
        if self.personal_details_page.is_element_visible(
            self.personal_details_page.nickname, timeout=ConfigReader.get_timeout("short")
        ):
            nickname = self.personal_details_page.get_nickname_value()
        if self.personal_details_page.is_element_visible(
            self.personal_details_page.blood_type, timeout=ConfigReader.get_timeout("short")
        ):
            blood_type = self.personal_details_page.get_blood_type_value()

        gender = next(
            (
                value
                for value in ("Male", "Female")
                if self.personal_details_page.is_gender_selected(value)
            ),
            None,
        )
        return {"nickname": nickname, "blood_type": blood_type, "gender": gender}

    def _capture_contact_details(self):
        self.contact_details_page.open_contact_details()
        return {
            "street_1": self.contact_details_page.get_field_value(
                self.contact_details_page.street_1
            ),
            "city": self.contact_details_page.get_field_value(
                self.contact_details_page.city
            ),
            "mobile": self.contact_details_page.get_field_value(
                self.contact_details_page.mobile
            ),
        }

    def _restore_my_info(self):
        if not self._my_info_changed:
            return

        cleanup_errors = []

        try:
            self._restore_personal_details()
        except Exception as error:
            cleanup_errors.append(("Personal Details", error))
            logger.warning("Could not restore Personal Details: %s", error)

        try:
            self._restore_contact_details()
        except Exception as error:
            cleanup_errors.append(("Contact Details", error))
            logger.warning("Could not restore Contact Details: %s", error)

        try:
            self._remove_created_emergency_contacts()
        except Exception as error:
            cleanup_errors.append(("Emergency Contacts", error))
            logger.warning("Could not clean up Emergency Contacts: %s", error)

        if cleanup_errors:
            sections = ", ".join(section for section, _ in cleanup_errors)
            logger.warning(
                "My Info cleanup finished with errors in: %s",
                sections,
            )

    def _restore_personal_details(self):
        self.dashboard_page.navigate_to_my_info_page()
        self.personal_details_page.open_personal_details()
        if self._personal_snapshot["nickname"] is not None:
            self.personal_details_page.enter_nickname_if_available(
                self._personal_snapshot["nickname"]
            )
        if self._personal_snapshot["gender"]:
            self.personal_details_page.select_gender(
                self._personal_snapshot["gender"]
            )
        if self._personal_snapshot["blood_type"]:
            self.personal_details_page.select_blood_type_if_available(
                self._personal_snapshot["blood_type"]
            )
        self.personal_details_page.save()

    def _restore_contact_details(self):
        self.dashboard_page.navigate_to_my_info_page()
        self.contact_details_page.open_contact_details()
        self.contact_details_page.enter_street_1(
            self._contact_snapshot["street_1"]
        )
        self.contact_details_page.enter_city(self._contact_snapshot["city"])
        self.contact_details_page.enter_mobile(self._contact_snapshot["mobile"])
        self.contact_details_page.save()

    def _remove_created_emergency_contacts(self):
        if not self._created_emergency_contacts:
            return

        self.dashboard_page.navigate_to_my_info_page()
        self.emergency_contacts_page.open_emergency_contacts()
        existing_rows = self.emergency_contacts_page.get_emergency_rows_text()
        for name in self._created_emergency_contacts:
            if any(name in row for row in existing_rows):
                self.emergency_contacts_page.delete_emergency_contact(name)

    # --- Personal details tests ---

    @pytest.mark.view_personal_info
    @allure.title("TC01 - View personal information")
    def test_view_personal_information(self):
        with allure.step("Open the Personal Details tab"):
            assert self.personal_details_page.open(), "Personal Details heading is not displayed"

        with allure.step("Verify that the basic information fields are displayed"):
            assert self.personal_details_page.is_displayed(self.personal_details_page.first_name), \
                "First Name field is not displayed"
            assert self.personal_details_page.is_gender_control_visible(), \
                "Gender radio buttons are not displayed"

    @pytest.mark.update_personal_info
    @allure.title("TC02 - Update Personal Details (nickname, gender, blood type)")
    def test_update_personal_details(self):
        self._my_info_changed = True
        nickname = TestData.generate_employee_name("Nick")
        personal_data = ConfigReader.get_my_info_data("personal_details")

        with allure.step("Open the Personal Details tab"):
            self.personal_details_page.open_personal_details()

        with allure.step(f"Enter nickname '{nickname}' if the field exists"):
            nickname_entered = self.personal_details_page.enter_nickname_if_available(nickname)

        with allure.step(f"Select Gender = {personal_data['gender']}"):
            self.personal_details_page.select_gender(personal_data["gender"])

        with allure.step(f"Select Blood Type = {personal_data['blood_type']} if the field exists"):
            blood_type_entered = self.personal_details_page.select_blood_type_if_available(
                personal_data["blood_type"]
            )

        with allure.step("Click Save"):
            self.personal_details_page.save()

        with allure.step("Verify that the updated values persisted"):
            assert self.personal_details_page.is_gender_selected(personal_data["gender"]), \
                f"Gender was not updated to {personal_data['gender']}"

        if nickname_entered:
            with allure.step("Verify that Nickname was saved with the expected value"):
                assert self.personal_details_page.get_nickname_value() == nickname, \
                    "Nickname value does not match input"

        if blood_type_entered:
            with allure.step("Verify Blood Type was saved with the expected value"):
                assert (
                    self.personal_details_page.get_blood_type_value()
                    == personal_data["blood_type"]
                ), "Blood Type value does not match input"

    # --- Contact and emergency contact tests ---

    @pytest.mark.update_contact_info
    @allure.title("TC03 - Update Contact Details (address, phone number)")
    def test_update_contact_details(self):
        self._my_info_changed = True
        contact_data = ConfigReader.get_my_info_data("contact")

        with allure.step("Open the Contact Details tab"):
            self.contact_details_page.open_contact_details()

        with allure.step("Enter the address (Street 1, City)"):
            self.contact_details_page.enter_street_1(contact_data["street_1"])
            self.contact_details_page.enter_city(contact_data["city"])

        with allure.step("Enter the phone number (Mobile)"):
            self.contact_details_page.enter_mobile(contact_data["mobile"])

        with allure.step("Click Save"):
            self.contact_details_page.save()

        with allure.step("Verify that the updated values persisted"):
            assert self.contact_details_page.get_mobile_value() == contact_data["mobile"], \
                "Mobile value does not match input after save"

        with allure.step("Verify that the address was saved correctly"):
            assert self.contact_details_page.get_field_value(
                self.contact_details_page.street_1
            ) == contact_data["street_1"], "Street 1 value does not match input"
            assert self.contact_details_page.get_field_value(
                self.contact_details_page.city
            ) == contact_data["city"], "City value does not match input"

    @pytest.mark.add_emergency_contact
    @allure.title("TC04 - Add an Emergency Contact")
    def test_add_emergency_contact(self):
        self._my_info_changed = True
        name = TestData.generate_employee_name("Emergency")
        emergency_data = ConfigReader.get_my_info_data("emergency_contact")

        with allure.step("Open the Emergency Contacts tab"):
            self.emergency_contacts_page.open_emergency_contacts()

        with allure.step("Click Add to open the creation form"):
            assert self.emergency_contacts_page.add_emergency_contact(), \
                "Save Emergency Contact form is not displayed"

        with allure.step(f"Enter emergency contact details: {name}"):
            self._created_emergency_contacts.append(name)
            self.emergency_contacts_page.enter_emergency_contact(
                name,
                emergency_data["relationship"],
                emergency_data["mobile"],
            )

        with allure.step("Click Save"):
            self.emergency_contacts_page.save()

        with allure.step("Verify that the new contact was persisted in the list"):
            assert self.emergency_contacts_page.wait_for_emergency_contact(name), \
                f"New emergency contact '{name}' not found in list"

    @pytest.mark.emergency_contact_required
    @allure.title("TC05 - Submit a missing required field and show an error")
    def test_emergency_contact_required_field(self):
        with allure.step("Open the Emergency Contacts tab"):
            self.emergency_contacts_page.open_emergency_contacts()

        with allure.step("Click Add without entering any data"):
            self.emergency_contacts_page.add_emergency_contact()

        with allure.step("Click Save"):
            self.emergency_contacts_page.save()

        with allure.step("Verify that the Required error is displayed"):
            assert self.emergency_contacts_page.has_required_error(), \
                "Required validation was not displayed"

    @pytest.mark.invalid_phone
    @allure.title("TC06 - Enter letters in the phone number and show an error")
    def test_contact_details_invalid_phone_format(self):
        self._my_info_changed = True
        validation_data = ConfigReader.get_my_info_data("validation")
        invalid_mobile = validation_data["invalid_mobile"]

        with allure.step("Open the Contact Details tab"):
            self.contact_details_page.open_contact_details()

        with allure.step(f"Enter an invalid phone number: '{invalid_mobile}'"):
            self.contact_details_page.enter_mobile(invalid_mobile)

        with allure.step("Click Save"):
            self.contact_details_page.save()

        with allure.step("Verify that the phone validation error is displayed"):
            assert "allows numbers" in self.contact_details_page.get_mobile_error_text().casefold(), \
                "Mobile validation error was not displayed"

        with allure.step("Verify that no successful save toast is displayed"):
            assert not self.contact_details_page.is_element_visible(
                self.contact_details_page.success_toast,
                timeout=ConfigReader.get_timeout("short"),
            ), "Save should not succeed with invalid phone number"

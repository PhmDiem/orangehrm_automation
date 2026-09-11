import allure
import pytest

from pages.dashboard_page import DashboardPage
from pages.my_info.personal_details_page import PersonalDetailsPage
from pages.my_info.contact_details_page import ContactDetailsPage
from pages.my_info.emergency_contacts_page import EmergencyContactsPage
from utils.config_reader import ConfigReader
from utils.test_data import TestData

@pytest.mark.my_info
class TestMyInfo:
    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.personal_details_page = PersonalDetailsPage(driver)
        self.contact_details_page = ContactDetailsPage(driver)
        self.emergency_contacts_page = EmergencyContactsPage(driver)

        self.dashboard_page.navigate_to_my_info_page()
        assert self.personal_details_page.open(), "My Info page is not displayed"

    @allure.title("TC01 - Xem thông tin cá nhân")
    def test_view_personal_information(self):
        with allure.step("Mở tab Personal Details"):
            assert self.personal_details_page.open(), "Personal Details heading is not displayed"

        with allure.step("Verify các trường thông tin cơ bản hiển thị"):
            assert self.personal_details_page.is_displayed(self.personal_details_page.first_name), \
                "First Name field is not displayed"
            assert self.personal_details_page.is_gender_control_visible(), \
                "Gender radio buttons are not displayed"

    @allure.title("TC02 - Cập nhật Personal Details (nickname, gender, blood type)")
    def test_update_personal_details(self):
        nickname = TestData.generate_employee_name("Nick")
        personal_data = ConfigReader.get_my_info_data("personal_details")

        with allure.step("Mở tab Personal Details"):
            self.personal_details_page.open_personal_details()

        with allure.step(f"Nhập nickname '{nickname}' (nếu field tồn tại)"):
            nickname_entered = self.personal_details_page.enter_nickname_if_available(nickname)

        with allure.step(f"Chọn Gender = {personal_data['gender']}"):
            self.personal_details_page.select_gender(personal_data["gender"])

        with allure.step(f"Chọn Blood Type = {personal_data['blood_type']} (nếu field tồn tại)"):
            self.personal_details_page.select_blood_type_if_available(
                personal_data["blood_type"]
            )

        with allure.step("Bấm Save"):
            self.personal_details_page.save()

        with allure.step("Verify lưu thành công"):
            assert self.personal_details_page.is_saved(), "Personal Details save was not confirmed"

        with allure.step("Verify Gender đã được chọn đúng"):
            assert self.personal_details_page.is_gender_selected(personal_data["gender"]), \
                f"Gender was not updated to {personal_data['gender']}"

        if nickname_entered:
            with allure.step("Verify Nickname được lưu đúng giá trị"):
                assert self.personal_details_page.get_nickname_value() == nickname, \
                    "Nickname value does not match input"

    @allure.title("TC03 - Cập nhật Contact Details (địa chỉ, số điện thoại)")
    def test_update_contact_details(self):
        contact_data = ConfigReader.get_my_info_data("contact")

        with allure.step("Mở tab Contact Details"):
            self.contact_details_page.open_contact_details()

        with allure.step("Nhập địa chỉ (Street 1, City)"):
            self.contact_details_page.enter_street_1(contact_data["street_1"])
            self.contact_details_page.enter_city(contact_data["city"])

        with allure.step("Nhập số điện thoại (Mobile)"):
            self.contact_details_page.enter_mobile(contact_data["mobile"])

        with allure.step("Bấm Save"):
            self.contact_details_page.save()

        with allure.step("Verify lưu thành công"):
            assert self.contact_details_page.is_saved(), "Contact Details save was not confirmed"

        with allure.step("Verify số điện thoại được lưu đúng giá trị"):
            assert self.contact_details_page.get_mobile_value() == contact_data["mobile"], \
                "Mobile value does not match input after save"

    @allure.title("TC04 - Thêm Emergency Contact")
    def test_add_emergency_contact(self):
        name = TestData.generate_employee_name("Emergency")
        emergency_data = ConfigReader.get_my_info_data("emergency_contact")

        with allure.step("Mở tab Emergency Contacts"):
            self.emergency_contacts_page.open_emergency_contacts()

        with allure.step("Bấm Add để mở form thêm mới"):
            assert self.emergency_contacts_page.add_emergency_contact(), \
                "Save Emergency Contact form is not displayed"

        with allure.step(f"Nhập thông tin liên hệ khẩn cấp: {name}"):
            self.emergency_contacts_page.enter_emergency_contact(
                name,
                emergency_data["relationship"],
                emergency_data["mobile"],
            )

        with allure.step("Bấm Save"):
            self.emergency_contacts_page.save()

        with allure.step("Verify lưu thành công"):
            assert self.emergency_contacts_page.is_saved(), "Emergency Contact save was not confirmed"

        with allure.step("Verify contact mới xuất hiện trong danh sách"):
            assert self.emergency_contacts_page.wait_for_emergency_contact(name), \
                f"New emergency contact '{name}' not found in list"

    @allure.title("TC05 - Cập nhật thiếu field bắt buộc → hiện lỗi")
    def test_emergency_contact_required_field(self):
        with allure.step("Mở tab Emergency Contacts"):
            self.emergency_contacts_page.open_emergency_contacts()

        with allure.step("Bấm Add nhưng không nhập gì"):
            self.emergency_contacts_page.add_emergency_contact()

        with allure.step("Bấm Save"):
            self.emergency_contacts_page.save()

        with allure.step("Verify hiện lỗi Required"):
            assert self.emergency_contacts_page.has_required_error(), \
                "Required validation was not displayed"

    @allure.title("TC06 - Nhập số điện thoại chứa chữ cái → hiện lỗi")
    def test_contact_details_invalid_phone_format(self):
        validation_data = ConfigReader.get_my_info_data("validation")
        invalid_mobile = validation_data["invalid_mobile"]

        with allure.step("Mở tab Contact Details"):
            self.contact_details_page.open_contact_details()

        with allure.step(f"Nhập số điện thoại không hợp lệ: '{invalid_mobile}'"):
            self.contact_details_page.enter_mobile(invalid_mobile)

        with allure.step("Bấm Save"):
            self.contact_details_page.save()

        with allure.step("Verify hiện lỗi validate số điện thoại"):
            assert self.contact_details_page.has_field_error(), \
                "Validation error for invalid phone number was not displayed"

        with allure.step("Verify không có toast lưu thành công"):
            assert not self.contact_details_page.is_element_visible(
                self.contact_details_page.success_toast,
                timeout=ConfigReader.get_timeout("short"),
            ), "Save should not succeed with invalid phone number"

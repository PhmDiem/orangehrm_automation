import allure
import pytest
from selenium.webdriver.common.by import By

from pages.dashboard_page import DashboardPage
from pages.my_info.my_info_page import MyInfoPage
from utils.config_reader import ConfigReader
from utils.test_data import TestData


class TestMyInfo:
    @pytest.fixture(autouse=True)
    def setup(self, driver, login):
        self.dashboard_page = DashboardPage(driver)
        self.my_info_page = MyInfoPage(driver)
        self.dashboard_page.navigate_to_my_info_page()
        assert self.my_info_page.open(), "My Info page is not displayed"

    @allure.title("TC01 - View personal information")
    def test_view_personal_information(self):
        assert self.my_info_page.is_displayed(
            self.my_info_page.personal_details_heading
        )

    @allure.title("TC02 - Update Personal Details")
    def test_update_personal_details(self):
        nickname = TestData.generate_employee_name("Nick")

        self.my_info_page.open_personal_details()
        self.my_info_page.enter_nickname(nickname)
        self.my_info_page.select_gender("Female")
        self.my_info_page.select_blood_type_if_available("O+")
        self.my_info_page.save()

        assert self.my_info_page.is_saved(), "Personal Details save was not confirmed"

    @allure.title("TC03 - Update Contact Details")
    def test_update_contact_details(self):
        contact_data = ConfigReader.get_my_info_data("contact")

        self.my_info_page.open_contact_details()
        self.my_info_page.send_keys(
            (By.XPATH, "//label[normalize-space()='Street 1']/following::input[1]"),
            contact_data["street_1"],
        )
        self.my_info_page.send_keys(
            (By.XPATH, "//label[normalize-space()='City']/following::input[1]"),
            contact_data["city"],
        )
        self.my_info_page.send_keys(
            (By.XPATH, "//label[normalize-space()='Mobile']/following::input[1]"),
            contact_data["mobile"],
        )
        self.my_info_page.save()

        assert self.my_info_page.is_saved(), "Contact Details save was not confirmed"

    @allure.title("TC04 - Add Emergency Contact")
    def test_add_emergency_contact(self):
        name = TestData.generate_employee_name("Emergency")
        emergency_data = ConfigReader.get_my_info_data("emergency_contact")
        self.my_info_page.open_emergency_contacts()
        self.my_info_page.add_emergency_contact()
        self.my_info_page.enter_emergency_contact(
            name,
            emergency_data["relationship"],
            emergency_data["mobile"],
        )
        self.my_info_page.save()

        assert self.my_info_page.is_saved(), "Emergency Contact save was not confirmed"
        assert any(name in row for row in self.my_info_page.get_emergency_rows_text())

    @allure.title("TC05 - Required field validation")
    def test_emergency_contact_required_field(self):
        self.my_info_page.open_emergency_contacts()
        self.my_info_page.add_emergency_contact()
        self.my_info_page.save()

        assert self.my_info_page.has_required_error(), (
            "Required validation was not displayed"
        )

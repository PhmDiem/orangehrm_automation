import allure
import pytest
import logging

from pages.dashboard_page import DashboardPage
from pages.pim.add_emloyee_page import CreateEmployee
from pages.pim.employee_page import EmployeePage
from pages.pim.employee_list_page import PIMPage
from utils.config_reader import ConfigReader
from utils.test_data import TestData

logger = logging.getLogger(__name__)


@pytest.mark.pim
class TestEmployeeManagement:

    @pytest.fixture(autouse=True)
    def setup(self, driver, login, request):
        self._created_employees = []
        self.dashboard_page = DashboardPage(driver)
        self.pim_page = PIMPage(driver)
        self.create_employee_page = CreateEmployee(driver)
        self.employee_page = EmployeePage(driver)
        request.addfinalizer(self._cleanup_created_employees)

    def _cleanup_created_employees(self):
        for first_name, last_name in self._created_employees:
            try:
                self._navigate_to_pim()
                self._search_employee_by_name(first_name, last_name)
                if self.pim_page.is_no_records_found_displayed():
                    continue
                self.pim_page.delete_first_row_with_bulk_action()
                self.pim_page.confirm_delete()
                self.pim_page.wait_for_loading_to_disappear()
            except Exception as error:
                logger.warning(
                    "Could not clean up employee '%s %s': %s",
                    first_name,
                    last_name,
                    error,
                )

    def _navigate_to_pim(self):
        self.dashboard_page.navigate_to_pim_page()

    def _create_employee(self, first_name, last_name):
        self.pim_page.navigate_to_add_employee()
        employee_id = self.create_employee_page.create_employee(first_name, last_name)
        self._created_employees.append((first_name, last_name))
        return employee_id

    def _create_employee_data(self):
        return (
            TestData.generate_employee_name("Auto"),
            TestData.generate_employee_name("Tester"),
        )

    def _search_employee_by_name(self, first_name, last_name):
        self.pim_page.search_by_employee_name(f"{first_name} {last_name}")

    def _assert_employee_name(
        self, first_name, last_name, message_prefix="Employee"
    ):
        displayed_name = self.employee_page.get_displayed_full_name()
        assert first_name in displayed_name and last_name in displayed_name, (
            f"{message_prefix} name mismatch. "
            f"Expected to contain '{first_name} {last_name}', got '{displayed_name}'"
        )

    @pytest.mark.view_employees
    @allure.title("View list of employees")
    def test_view_list_of_employees(self):
        with allure.step("Navigate to PIM page"):
            self._navigate_to_pim()

        with allure.step("Verify employee list is displayed"):
            assert (
                self.pim_page.is_employees_list_displayed()
            ), "Employee list is not displayed"

        with allure.step("Verify at least one employee record exists"):
            assert (
                self.pim_page.get_employee_row_count() > 0
            ), "Employee list is empty"

    @pytest.mark.new_employee
    @allure.title("Create a new employee with First/Last name")
    def test_create_new_employee(self):
        first_name, last_name = self._create_employee_data()

        with allure.step("Navigate to PIM page"):
            self._navigate_to_pim()

        with allure.step("Navigate to Add Employee page"):
            self.pim_page.navigate_to_add_employee()

        with allure.step(f"Create new employee: {first_name} {last_name}"):
            emp_id = self.create_employee_page.create_employee(
                first_name, last_name
            )
            self._created_employees.append((first_name, last_name))

        with allure.step("Verify Personal Details page is displayed"):
            assert (
                self.employee_page.is_personal_details_displayed()
            ), "Personal Details page is not displayed after creation"

        with allure.step("Verify created employee data is correct"):
            self._assert_employee_name(first_name, last_name)

        with allure.step("Verify Employee ID was auto-generated before save"):
            assert (
                emp_id and emp_id.strip() != ""
            ), "Employee ID was not auto-generated"

    @pytest.mark.without_name
    @pytest.mark.parametrize("missing_field", ["first_name", "last_name"])
    @allure.title("Create employee with missing {missing_field}")
    def test_create_employee_missing_name(self, missing_field):
        first_name = TestData.generate_employee_name("Auto")
        last_name = TestData.generate_employee_name("Tester")

        with allure.step("Navigate to PIM > Add Employee"):
            self._navigate_to_pim()
            self.pim_page.navigate_to_add_employee()

        with allure.step(f"Leave {missing_field} empty and submit the form"):
            self.create_employee_page.wait_for_loading_to_disappear()
            if missing_field == "first_name":
                self.create_employee_page.enter_last_name(last_name)
            else:
                self.create_employee_page.enter_first_name(first_name)
            self.create_employee_page.click_save()

        with allure.step(f"Verify {missing_field} required error is displayed"):
            if missing_field == "first_name":
                assert self.create_employee_page.is_first_name_error_displayed()
            else:
                assert self.create_employee_page.is_last_name_error_displayed()

        with allure.step(
            "Verify page did not navigate away (employee not created)"
        ):
            assert (
                not self.employee_page.is_personal_details_displayed_immediate()
            ), "Employee was created despite missing Last Name"

    @pytest.mark.search_by_name
    @allure.title("Search employee by name")
    def test_search_by_employee_name(self):
        first_name, last_name = self._create_employee_data()

        with allure.step(
            "Navigate to PIM and create an employee to search for"
        ):
            self._navigate_to_pim()
            self._create_employee(first_name, last_name)

        with allure.step("Navigate back to Employee List"):
            self.employee_page.navigate_to_employee_list()

        with allure.step(f"Search by employee name: {first_name} {last_name}"):
            self._search_employee_by_name(first_name, last_name)

        with allure.step("Verify search result contains the created employee"):
            assert (
                self.pim_page.is_employee_row_displayed(
                    f"{first_name} {last_name}"
                )
            ), f"Search result did not contain '{first_name} {last_name}'"

    @pytest.mark.search_by_id
    @allure.title("Search employee by Employee ID")
    def test_search_by_employee_id(self):
        first_name, last_name = self._create_employee_data()

        with allure.step(
            "Navigate to PIM and create an employee to search for"
        ):
            self._navigate_to_pim()
            self.pim_page.navigate_to_add_employee()
            emp_id = self.create_employee_page.create_employee(
                first_name, last_name
            )
            self._created_employees.append((first_name, last_name))

        with allure.step("Navigate back to Employee List"):
            self.employee_page.navigate_to_employee_list()

        with allure.step(f"Search by Employee ID: {emp_id}"):
            self.pim_page.search_by_employee_id(emp_id)

        with allure.step("Verify search result contains the created employee"):
            assert self.pim_page.is_employee_row_displayed(
                f"{emp_id} {first_name}"
            ), (
                f"Search result did not contain ID '{emp_id}' and "
                f"name '{first_name}'"
            )

    @pytest.mark.search_no_results
    @allure.title("Search employee with no matching results")
    def test_search_no_results(self):
        no_result_id = ConfigReader.get_employee_data("searchNoResult")[
            "employeeId"
        ]

        with allure.step("Navigate to Employee List"):
            self._navigate_to_pim()

        with allure.step(
            f"Search for a non-existent employee ID: {no_result_id}"
        ):
            self.pim_page.search_by_employee_id(no_result_id)

        with allure.step("Verify 'No Records Found' is displayed"):
            assert self.pim_page.wait_for_no_records_found(), (
                "Expected No Records Found and an empty employee table"
            )

    @pytest.mark.view_profile
    @allure.title("View employee profile")
    def test_view_employee_profile(self):
        first_name, last_name = self._create_employee_data()

        with allure.step("Create an employee to view"):
            self._navigate_to_pim()
            self._create_employee(first_name, last_name)

        with allure.step("Navigate back to PIM Employee List and search"):
            self.employee_page.navigate_to_employee_list()
            self._search_employee_by_name(first_name, last_name)

        with allure.step("Click on employee to view profile"):
            self.pim_page.click_first_employee_row()

        with allure.step(
            "Verify Personal Details page is displayed with correct name"
        ):
            assert (
                self.employee_page.is_personal_details_displayed()
            ), "Personal Details page is not displayed"
            self._assert_employee_name(first_name, last_name, "Profile")

    @pytest.mark.update_profile
    @allure.title("Update employee personal info (gender, DOB, blood type)")
    def test_update_employee_personal_info(self):
        first_name, last_name = self._create_employee_data()
        update_data = ConfigReader.get_employee_data("updateProfile")

        with allure.step("Create an employee to update"):
            self._navigate_to_pim()
            self._create_employee(first_name, last_name)
            assert self.employee_page.is_personal_details_displayed()

        with allure.step("Update gender, DOB, and blood type"):
            dob = update_data["dob"]
            self.employee_page.select_gender(update_data["gender"])
            self.employee_page.enter_dob(dob)
            if self.employee_page.is_blood_type_available():
                self.employee_page.select_blood_type(update_data["bloodType"])
            self.employee_page.click_save()

        with allure.step("Verify update success message is displayed"):
            assert (
                self.employee_page.is_update_success_displayed()
            ), "Update success message was not displayed"

        with allure.step("Verify DOB was saved correctly"):
            assert (
                self.employee_page.wait_for_dob_value(dob) == dob
            ), "DOB was not updated correctly"

    @pytest.mark.delete_employee
    @allure.title("Delete an employee")
    def test_delete_employee(self):
        first_name, last_name = self._create_employee_data()

        with allure.step("Create an employee to delete"):
            self._navigate_to_pim()
            self._create_employee(first_name, last_name)
            assert (
                self.employee_page.is_personal_details_displayed()
            ), "Employee was not created successfully"

        with allure.step(
            "Navigate back to PIM Employee List and search for the employee"
        ):
            self._navigate_to_pim()
            self._search_employee_by_name(first_name, last_name)

        with allure.step("Verify employee appears before deletion"):
            assert (
                self.pim_page.is_employee_row_displayed(
                    f"{first_name} {last_name}"
                )
            ), "Employee not found before deletion — cannot proceed"

        with allure.step("Delete the employee"):
            self.pim_page.delete_first_row_via_icon()
            self.pim_page.confirm_delete()
            self.pim_page.wait_for_loading_to_disappear()

        with allure.step("Verify employee row no longer exists in the table"):
            assert (
                self.pim_page.wait_for_employee_absent(
                    f"{first_name} {last_name}"
                )
            ), "Employee still appears after deletion"
            self._created_employees.remove((first_name, last_name))

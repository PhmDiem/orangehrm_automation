import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.config_reader import ConfigReader
from utils.test_data import TestData

logger = logging.getLogger(__name__)


class CreateEmployee(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.first_name = (By.NAME, "firstName")
        self.last_name = (By.NAME, "lastName")
        self.employee_id = (
            By.XPATH,
            '//label[text()="Employee Id"]/following::input[1]',
        )
        self.save_btn = (By.XPATH, '//button[@type="submit"]')
        self.employee_id_error = (
            By.XPATH,
            '//label[text()="Employee Id"]/following::span[contains(@class,"error-message")][1]',
        )
        self.first_name_error = (
            By.XPATH,
            '//input[@name="firstName"]/following::span[contains(@class,"error-message")][1]',
        )
        self.last_name_error = (
            By.XPATH,
            '//input[@name="lastName"]/following::span[contains(@class,"error-message")][1]',
        )

    def enter_first_name(self, first_name):
        self.send_keys(self.first_name, first_name)

    def enter_last_name(self, last_name):
        self.send_keys(self.last_name, last_name)

    def get_employee_id(self):
        return self.find_element(self.employee_id).get_attribute("value")

    def click_save(self):
        self.click(self.save_btn)

    def is_employee_id_duplicate_error_displayed(self, timeout=5):
        return self.is_element_visible(self.employee_id_error, timeout=timeout)

    def is_first_name_error_displayed(self):
        return self.is_element_visible(self.first_name_error, timeout=3)

    def is_last_name_error_displayed(self):
        return self.is_element_visible(self.last_name_error, timeout=3)

    def enter_employee_id(self, employee_id):
        self.send_keys(self.employee_id, employee_id)

    def create_employee(self, first_name, last_name, max_retries=3):
        for attempt in range(max_retries):
            logger.info(
                "Creating employee, attempt %s/%s", attempt + 1, max_retries
            )

            self.wait_for_loading_to_disappear()

            self.enter_first_name(first_name)
            self.enter_last_name(last_name)

            # Generate a new ID for each attempt.
            employee_id = TestData.generate_employee_id()

            logger.debug("Generated employee ID: %s", employee_id)

            self.enter_employee_id(employee_id)

            # Verify that the ID was entered into the input.
            actual_id = self.get_employee_id()

            logger.debug("Actual employee ID in input: %s", actual_id)

            if actual_id != employee_id:
                raise Exception(
                    f"Employee ID was not entered correctly. "
                    f"Expected={employee_id}, Actual={actual_id}"
                )

            self.click_save()

            # Duplicate?
            if self.is_employee_id_duplicate_error_displayed(
                timeout=ConfigReader.get_timeout("medium")
            ):
                logger.warning("Employee ID %s is duplicated", employee_id)

                if attempt < max_retries - 1:
                    logger.info(
                        "Refreshing before generating a new employee ID"
                    )
                    self.driver.refresh()
                    continue

                raise Exception(
                    f"Employee ID '{employee_id}' is duplicated "
                    f"after {max_retries} attempts"
                )

            # Save completed successfully.
            logger.info("Employee %s created successfully", employee_id)

            WebDriverWait(
                self.driver, ConfigReader.get_timeout("page_load")
            ).until(
                lambda d: "addEmployee" not in d.current_url
            )

            return employee_id

        raise Exception(f"Cannot create employee after {max_retries} attempts")

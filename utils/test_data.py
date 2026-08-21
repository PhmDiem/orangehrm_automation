import random
import string
import time


class TestData:

    DEFAULT_ROLE = "ESS"
    DEFAULT_STATUS = "Enabled"
    DEFAULT_PASSWORD = "Test@123"

    @staticmethod
    def generate_username(prefix="test_user"):
        timestamp = int(time.time() * 1000)
        return f"{prefix}_{timestamp}"

    @staticmethod
    def generate_random_username(prefix="test_user", length=6):
        suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=length)
        )
        return f"{prefix}_{suffix}"

        # ==== PIM ====

    DEFAULT_GENDER = "Male"
    DEFAULT_BLOOD_TYPE = "O+"
    DEFAULT_DOB = "1995-05-10"

    @staticmethod
    def generate_employee_name(prefix="TestEmp"):
        timestamp = int(time.time() * 10)
        return f"{prefix}_{timestamp}"

    @staticmethod
    def generate_employee_id(length=4):
        return "".join(random.choices(string.digits, k=length))

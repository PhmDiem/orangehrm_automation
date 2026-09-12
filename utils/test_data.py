import random
import string
from uuid import uuid4
from datetime import datetime, timedelta


class TestData:

    # --- User defaults and generators ---

    DEFAULT_ROLE = "ESS"
    DEFAULT_STATUS = "Enabled"

    @staticmethod
    def generate_username(prefix="test_user"):
        return f"{prefix}_{uuid4().hex[:12]}"

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
        return f"{prefix}_{uuid4().hex[:12]}"

    @staticmethod
    def generate_employee_id(length=8):
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def generate_future_leave_dates(min_days=5, max_days=100, duration_days=2):
        """
        Return (from_date, to_date) with a random future offset instead of a
        fixed days_from_now=7. A fixed offset would create the same request
        date on every run in a day; leftover requests would then cause
        'Overlapping Leave Request(s) Found' on every rerun.
        max_days=100 keeps the date within the default Leave Period, which is
        usually the current calendar year.
        """
        today = datetime.now().date()
        latest_start = datetime(today.year, 12, 31).date() - timedelta(
            days=duration_days
        )
        maximum_offset = min(max_days, (latest_start - today).days)
        if maximum_offset < min_days:
            raise ValueError("No valid leave dates remain in the current leave period")

        days_from_now = random.randint(min_days, maximum_offset)
        start = datetime.now() + timedelta(days=days_from_now)
        end = start + timedelta(days=duration_days)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    @staticmethod
    def generate_past_leave_dates(days_ago=30, duration_days=2):
        """Return an invalid range where To Date is before From Date.

        OrangeHRM allows both dates to be in the past, so TC03 must validate
        the date-range rule instead of relying on past dates alone.
        """
        start = datetime.now() - timedelta(days=days_ago)
        end = start - timedelta(days=duration_days)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    @staticmethod
    def calculate_days_needed(from_date: str, to_date: str) -> int:
        """Calculate the inclusive number of days for comparison with balance."""
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        return (end - start).days + 1

    @staticmethod
    def to_ui_date_format(iso_date: str) -> str:
        """Convert YYYY-MM-DD to OrangeHRM's actual UI format: YYYY-DD-MM."""
        year, month, day = iso_date.split("-")
        return f"{year}-{day}-{month}"

    @staticmethod
    def generate_unique_marker(prefix="AUTOTEST"):
        """Create a unique marker for a test request's Comments field.

        The marker identifies the newly created request when dates may repeat
        because of randomization or repeated test runs.
        """
        return f"{prefix}_{uuid4().hex[:12]}"

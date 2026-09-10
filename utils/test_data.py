import random
import string
import time
from datetime import datetime, timedelta


class TestData:

    DEFAULT_ROLE = "ESS"
    DEFAULT_STATUS = "Enabled"

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

    @staticmethod
    def generate_future_leave_dates(min_days=5, max_days=100, duration_days=2):
        """
        Trả về (from_date, to_date) với offset NGẪU NHIÊN trong tương lai
        (thay vì cố định days_from_now=7). Offset cố định khiến MỌI lần chạy
        test trong cùng 1 ngày luôn tạo request trùng y hệt ngày với lần chạy
        trước đó, và vì leave request cũ không được dọn dẹp, nó luôn gây ra
        lỗi 'Overlapping Leave Request(s) Found' 100% khi chạy lại.
        max_days=100 để không vượt ra ngoài Leave Period mặc định (thường là
        1 năm dương lịch hiện tại)."""
        days_from_now = random.randint(min_days, max_days)
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
        """Tính số ngày giữa from_date và to_date (inclusive), dùng để so sánh với balance."""
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        return (end - start).days + 1

    @staticmethod
    def to_ui_date_format(iso_date: str) -> str:
        """Convert YYYY-MM-DD sang format UI thực tế của OrangeHRM: YYYY-DD-MM."""
        year, month, day = iso_date.split("-")
        return f"{year}-{day}-{month}"

    @staticmethod
    def generate_unique_marker(prefix="AUTOTEST"):
        """Chuỗi duy nhất để đánh dấu 1 request test cụ thể, dùng trong ô Comments
        nhằm verify chính xác đúng request vừa tạo, tránh nhầm với request khác
        dù có thể trùng ngày tháng (do random hoặc do chạy lại nhiều lần)."""
        timestamp = int(time.time() * 1000)
        return f"{prefix}_{timestamp}"

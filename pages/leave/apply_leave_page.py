import logging
import re
from datetime import datetime
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from utils.config_reader import ConfigReader

logger = logging.getLogger(__name__)


class ApplyLeavePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.entitlements_menu = (By.XPATH, '//span[normalize-space(.)="Entitlements"]')
        self.add_entitlement_link = (By.XPATH, '//a[text()="Add Entitlements"]')
        self.apply_leave_header = (By.XPATH, '//h6[text()="Apply Leave"]')
        self.leave_type_dropdown = (By.XPATH, "//label[text()='Leave Type']/../..//div[contains(@class,'oxd-select-text')]")
        self.leave_type_options = (By.CSS_SELECTOR, ".oxd-select-dropdown .oxd-select-option")
        self.from_date_input = (By.XPATH, "(//label[text()='From Date']/../..//input)[1]")
        self.to_date_input = (By.XPATH, "(//label[text()='To Date']/../..//input)[1]")
        self.apply_btn = (By.XPATH, "//button[@type='submit']")
        self.error_messages = (By.CSS_SELECTOR, ".oxd-input-field-error-message")
        self.toast_content = (By.CSS_SELECTOR, ".oxd-toast-content")
        self.toast_success = (By.CSS_SELECTOR, ".oxd-toast--success")
        self.no_leave_balance_message = (
            By.XPATH, "//p[text()='No Leave Types with Leave Balance']"
        )
        # Xuất hiện khi ngày apply trùng với 1 leave request khác đã tồn tại
        # (thường là leftover từ lần chạy test trước, chưa bị hủy/duyệt).
        self.overlap_warning_header = (
            By.XPATH, "//*[normalize-space(text())='Overlapping Leave Request(s) Found']"
        )
        self.my_leave_btn = (By.XPATH, '//a[normalize-space()="My Leave"]')
        self.comments_input = (By.XPATH, "//textarea")

        self.leave_balance_value = (
            By.XPATH, "//label[text()='Leave Balance']/following::p[1]"
        )

        # --- Calendar popup locators ---
        self.calendar_month_label = (By.CSS_SELECTOR, ".oxd-calendar-selector-month-selected p")
        self.calendar_year_label = (By.CSS_SELECTOR, ".oxd-calendar-selector-year-selected p")
        self.calendar_prev_btn = (By.CSS_SELECTOR, ".oxd-calendar-header button:first-child")
        self.calendar_next_btn = (By.CSS_SELECTOR, ".oxd-calendar-header button:last-child")
        self.calendar_date_cells = (By.CSS_SELECTOR, ".oxd-calendar-date-wrapper .oxd-calendar-date")

    def is_page_displayed(self):
        return self.is_displayed(self.apply_leave_header)

    def navigate_to_add_entitlement(self):
        self.click(self.entitlements_menu)
        self.click(self.add_entitlement_link)

    def navigate_to_my_leave(self):
        self.click(self.my_leave_btn)

    def _to_ui_date_format(self, iso_date: str) -> str:
        """
        Convert ngày từ format chuẩn YYYY-MM-DD (dùng trong test data/leave_data.json)
        sang đúng format UI thực tế của OrangeHRM: YYYY-DD-MM
        (xác nhận qua placeholder 'yyyy-dd-mm' hiển thị trên form Apply Leave).
        """
        year, month, day = iso_date.split("-")
        return f"{year}-{day}-{month}"

    def select_date_via_calendar(self, date_input_locator, date_value: str):
        target = datetime.strptime(date_value, "%Y-%m-%d")

        self.click(date_input_locator)

        # Đợi calendar thực sự render xong (year label có giá trị, không rỗng)
        # trước khi bắt đầu đọc - tránh đọc trúng lúc DOM đang transition
        self.wait.until(
            lambda d: self.get_text(self.calendar_year_label).strip() != ""
        )

        for _ in range(60):
            current_month_text = self.get_text(self.calendar_month_label)
            current_year_text = self.get_text(self.calendar_year_label)
            current_month_num = datetime.strptime(current_month_text, "%B").month
            current_year_num = int(current_year_text)

            if current_year_num == target.year and current_month_num == target.month:
                break

            target_index = target.year * 12 + target.month
            current_index = current_year_num * 12 + current_month_num
            if target_index > current_index:
                self.click(self.calendar_next_btn)
            else:
                self.click(self.calendar_prev_btn)
        else:
            raise TimeoutError(f"Không thể điều hướng calendar tới {target.year}-{target.month:02d}")

        day_cells = self.find_elements(self.calendar_date_cells)
        for cell in day_cells:
            if cell.text.strip() == str(target.day):
                cell.click()
                break
        else:
            raise ValueError(f"Không tìm thấy ngày {target.day} trong calendar")

        # Đợi calendar đóng hẳn trước khi trả về, tránh popup còn sót lại
        # ảnh hưởng tới lần mở calendar tiếp theo (From Date -> To Date)
        self.wait.until(lambda d: len(d.find_elements(*self.calendar_date_cells)) == 0)

    def apply_leave(
        self,
        leave_type: str,
        from_date: str,
        to_date: str,
        comment: str = None,
        wait_for_feedback: bool = True,
    ):
        if leave_type:
            self.click(self.leave_type_dropdown)
            self.click_dropdown_option(self.leave_type_options, expected_text=leave_type)

        if from_date:
            self.select_date_via_calendar(self.from_date_input, from_date)

        if to_date:
            self.select_date_via_calendar(self.to_date_input, to_date)

        if comment:
            self.send_keys(self.comments_input, comment)

        self.click(self.apply_btn)
        if wait_for_feedback:
            # The demo application can persist a request without showing a
            # toast or error. Do not submit a second time: that would submit a
            # freshly reset form and create misleading "Required" errors.
            try:
                self._wait_for_apply_feedback(
                    timeout=ConfigReader.get_timeout("feedback")
                )
            except TimeoutException:
                return False
        return True

    def _wait_for_apply_feedback(self, timeout=None):
        """Wait for one of the mutually exclusive Apply Leave outcomes."""
        wait_time = timeout or ConfigReader.get_explicit_wait()
        return WebDriverWait(self.driver, wait_time).until(
            EC.any_of(
                EC.visibility_of_element_located(self.toast_success),
                EC.visibility_of_element_located(self.error_messages),
                EC.visibility_of_element_located(self.overlap_warning_header),
            )
        )

    def is_overlap_warning_shown(self) -> bool:
        """
        True nếu trang hiện banner 'Overlapping Leave Request(s) Found' - nghĩa là
        ngày vừa apply trùng với 1 leave request khác đã tồn tại từ trước (thường
        do leftover data từ lần chạy test trước chưa được dọn dẹp, KHÔNG phải lỗi
        thật của lần chạy hiện tại).
        """
        return self.is_element_visible(
            self.overlap_warning_header,
            timeout=ConfigReader.get_timeout("short"),
        )

    def apply_leave_avoiding_overlap(
        self, leave_type: str, date_generator, comment: str = None, max_attempts: int = 5
    ):
        """
        date_generator: callable() -> (from_date, to_date) theo format ISO
        'YYYY-MM-DD' (VD: TestData.generate_future_leave_dates). Mỗi lần thử
        gọi lại date_generator để lấy 1 cặp ngày MỚI.

        Tự động thử lại (tối đa max_attempts lần) nếu OrangeHRM báo
        'Overlapping Leave Request' - tránh flaky do dữ liệu leftover từ các
        lần chạy test trước còn tồn đọng (không có cơ chế dọn dẹp trên demo
        site public). Trả về (from_date, to_date) đã áp dụng thành công.
        """
        last_dates = None
        for _ in range(max_attempts):
            from_date, to_date = date_generator()
            last_dates = (from_date, to_date)
            self.apply_leave(
                leave_type,
                from_date,
                to_date,
                comment=comment,
                wait_for_feedback=False,
            )

            if self.is_overlap_warning_shown():
                continue

            return from_date, to_date

        raise AssertionError(
            f"Vẫn bị 'Overlapping Leave Request' sau {max_attempts} lần thử với "
            f"ngày khác nhau. Ngày cuối cùng đã thử: {last_dates}"
        )

    def is_success_toast_visible(self):
        return self.is_element_visible(
            self.toast_success,
            timeout=ConfigReader.get_timeout("feedback"),
        )

    def get_error_messages(self):
        messages = []
        for locator in (self.error_messages, self.toast_content):
            try:
                messages.extend(
                    element.text.strip()
                    for element in self.driver.find_elements(*locator)
                    if element.is_displayed()
                    and element.text.strip()
                    and not (
                        locator == self.toast_content
                        and "success" in (element.get_attribute("class") or "").lower()
                    )
                )
            except Exception:
                continue
        return list(dict.fromkeys(messages))

    def get_current_balance(self, leave_type: str) -> float:
        self.click(self.leave_type_dropdown)
        self.click_dropdown_option(self.leave_type_options, expected_text=leave_type)

        try:
            balance_text = self.get_text(self.leave_balance_value)
        except Exception as e:
            logger.warning("Could not find leave balance value: %s", e)
            return 0.0

        match = re.search(r'([\d.]+)', balance_text)
        result = float(match.group(1)) if match else 0.0
        logger.debug("Parsed leave balance: %s", result)
        return result

    def has_no_leave_balance(self):
        """True nếu form Apply Leave báo không có leave type nào còn balance."""
        return self.is_element_visible(
            self.no_leave_balance_message,
            timeout=ConfigReader.get_timeout("medium"),
        )

    def has_leave_type_option(self, leave_type: str) -> bool:
        """
        Chỉ trả lời: 'CAN - Personal' có tồn tại trong dropdown Leave Type không.
        Không liên quan gì đến số ngày balance còn lại.
        """
        self.click(self.leave_type_dropdown)
        try:
            options = self.find_elements(self.leave_type_options)
            expected = self._normalize_text(leave_type)
            found = any(self._normalize_text(opt.text) == expected for opt in options)
        finally:
            self.click(self.apply_leave_header)  # đóng dropdown, click ra ngoài
        return found

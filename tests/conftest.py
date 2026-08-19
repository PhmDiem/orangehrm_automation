import os
from datetime import datetime
from tempfile import TemporaryDirectory

import allure
import pytest
from selenium import webdriver

from utils.config_reader import ConfigReader
from pages.login_page import LoginPage


def build_browser_options():
    options = webdriver.ChromeOptions()
    profile = TemporaryDirectory(prefix="orangehrm_")

    options.add_argument(f"--user-data-dir={profile.name}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument(
        "--disable-features=PasswordCheck,PasswordManagerOnboarding,"
        "AutofillServerCommunication"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.page_load_strategy = "eager"
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False,
        "useAutomationExtension": False,
    })

    if ConfigReader.is_headless():
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    return options, profile


@pytest.fixture(scope="function")
def driver():
    options, temp_profile = build_browser_options()
    driver = None
    try:
        browser = ConfigReader.get_browser().lower()
        if browser != "chrome":
            raise ValueError(f"Unsupported browser: {browser}")

        driver = webdriver.Chrome(options=options)
        explicit_wait = ConfigReader.get_explicit_wait()
        driver.set_page_load_timeout(explicit_wait)

        if not ConfigReader.is_headless():
            driver.maximize_window()

        driver.get(ConfigReader.get_url())
        yield driver

    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        try:
            temp_profile.cleanup()
        except Exception:
            pass

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Chỉ chụp ảnh và đính kèm vào Allure khi test bị FAIL
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            try:
                # Tạo thư mục lưu ảnh cục bộ
                screenshot_dir = "screenshots"
                os.makedirs(screenshot_dir, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{item.name}_{timestamp}.png"
                screenshot_path = os.path.join(screenshot_dir, file_name)

                # Lưu ảnh xuống máy
                driver.save_screenshot(screenshot_path)

                # Đính kèm ảnh trực tiếp vào Allure Report mà không cần mở lại file
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="Screenshot on Failure",
                    attachment_type=allure.attachment_type.PNG,
                )
                print(f"Đã chụp và đính kèm screenshot thành công: {file_name}")

            except Exception as e:
                print(f"Không thể xử lý screenshot: {e}")

@pytest.fixture
def login(driver):
    login_page = LoginPage(driver)
    user = ConfigReader.get_user("admin")
    login_page.login(user["username"], user["password"])
    return login_page
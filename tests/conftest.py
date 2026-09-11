import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage
from utils.allure_helper import attach_failure_screenshot
from utils.browser_options import build_chrome_options
from utils.config_reader import ConfigReader


@pytest.fixture(scope="function")
def driver():
    options, temp_profile = build_chrome_options()
    driver = None

    try:
        browser = ConfigReader.get_browser().strip().lower()

        if browser == "chrome":
            driver = webdriver.Chrome(
                options=options,
            )
        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                "Currently supported browsers: chrome"
            )

        driver.implicitly_wait(ConfigReader.get_implicit_wait())
        driver.set_page_load_timeout(ConfigReader.get_timeout("page_load"))

        if not ConfigReader.is_headless():
            driver.maximize_window()

        _open_login_page(driver)
        yield driver

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        temp_profile.cleanup()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver:
        attach_failure_screenshot(driver, item.name)


@pytest.fixture
def login(driver):
    user = ConfigReader.get_user("admin")
    login_page = LoginPage(driver)
    login_page.login(user["username"], user["password"])
    return login_page


def _open_login_page(driver, max_attempts=2):
    """Open the public demo login page, retrying transient renderer failures."""
    login_locator = (By.NAME, "username")

    for attempt in range(max_attempts):
        try:
            driver.get(ConfigReader.get_url())
            WebDriverWait(
                driver, ConfigReader.get_timeout("page_load")
            ).until(EC.presence_of_element_located(login_locator))
            return
        except TimeoutException:
            if attempt == max_attempts - 1:
                raise
            try:
                driver.execute_script("window.stop();")
            except Exception:
                pass
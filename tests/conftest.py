import pytest
from selenium import webdriver

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
            driver = webdriver.Chrome(options=options)
        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. "
                "Currently supported browsers: chrome"
            )

        driver.implicitly_wait(
            ConfigReader.get_implicit_wait()
        )

        driver.set_page_load_timeout(
            ConfigReader.get_explicit_wait()
        )

        if not ConfigReader.is_headless():
            driver.maximize_window()

        driver.get(ConfigReader.get_url())

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
        attach_failure_screenshot(
            driver,
            item.name,
        )


@pytest.fixture
def login(driver):
    user = ConfigReader.get_user("admin")

    login_page = LoginPage(driver)

    login_page.login(
        user["username"],
        user["password"],
    )

    return login_page
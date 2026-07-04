import pytest
from selenium import webdriver
from tempfile import TemporaryDirectory
from utils.config_reader import ConfigReader

@pytest.fixture(scope="function")
def driver():
    temp_profile = TemporaryDirectory(prefix="orangehrm_")
    
    options = webdriver.ChromeOptions()
    
    # --- Profile & Security ---
    options.add_argument(f"--user-data-dir={temp_profile.name}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-features=PasswordCheck,PasswordManagerOnboarding,AutofillServerCommunication")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.page_load_strategy = 'eager'

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False,
        "useAutomationExtension": False,
    })

    # --- Headless ---
    if ConfigReader.is_headless():
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        explicit_wait = ConfigReader.get_explicit_wait()
        driver.command_executor.set_timeout(explicit_wait)
        driver.implicitly_wait(ConfigReader.get_implicit_wait())
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
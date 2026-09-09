from tempfile import TemporaryDirectory

from selenium import webdriver

from utils.config_reader import ConfigReader


def build_chrome_options():
    options = webdriver.ChromeOptions()
    profile = TemporaryDirectory(prefix="orangehrm_")

    options.add_argument(f"--user-data-dir={profile.name}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")

    options.add_argument(
        "--disable-features="
        "PasswordCheck,"
        "PasswordManagerOnboarding,"
        "AutofillServerCommunication"
    )

    options.add_argument("--disable-blink-features=AutomationControlled")

    options.page_load_strategy = "eager"

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"],
    )

    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
            "useAutomationExtension": False,
        },
    )

    if ConfigReader.is_headless():
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    return options, profile

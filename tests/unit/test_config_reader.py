import pytest

from utils.config_reader import ConfigReader


pytestmark = pytest.mark.regression


# --- Timeout configuration ---

def test_page_load_timeout_uses_config_default(monkeypatch):
    monkeypatch.delenv("ORANGEHRM_PAGE_LOAD_TIMEOUT", raising=False)
    ConfigReader.reload()

    assert ConfigReader.get_timeout("page_load") == 15


def test_page_load_timeout_accepts_environment_override(monkeypatch):
    monkeypatch.setenv("ORANGEHRM_PAGE_LOAD_TIMEOUT", "42.5")

    assert ConfigReader.get_timeout("page_load") == 42.5


def test_timeout_rejects_non_numeric_environment_value(monkeypatch):
    monkeypatch.setenv("ORANGEHRM_PAGE_LOAD_TIMEOUT", "slow")

    with pytest.raises(ValueError, match="must be a number"):
        ConfigReader.get_timeout("page_load")


    # --- Credential overrides ---

def test_admin_credentials_accept_environment_overrides(monkeypatch):
    monkeypatch.setenv("ORANGEHRM_ADMIN_USERNAME", "ci-admin")
    monkeypatch.setenv("ORANGEHRM_ADMIN_PASSWORD", "ci-password")

    assert ConfigReader.get_user("admin") == {
        "username": "ci-admin",
        "password": "ci-password",
    }

import json
import os


class ConfigReader:
    """Load and cache shared JSON configuration files for the test framework."""

    _configs = {}

    # config_reader.py -> utils/ -> project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def load_file(file_key, folder_name, file_name):
        """Load one JSON file, caching it by key and raising clear errors."""
        if file_key not in ConfigReader._configs:
            file_path = os.path.join(
                ConfigReader.BASE_DIR, folder_name, file_name
            )

            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Configuration file not found: {file_path}")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ConfigReader._configs[file_key] = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"File '{file_path}' does not contain valid JSON: {e}"
                )

        return ConfigReader._configs[file_key]

    # --- Data accessors ---

    @staticmethod
    def get_config():
        return ConfigReader.load_file("config", "config", "config.json")

    @staticmethod
    def get_users():
        """Return users from data/users_data.json."""
        users_data = ConfigReader.load_file("users", "data", "users_data.json")
        return users_data.get("users", {})

    @staticmethod
    def get_employee_data(employee_type="searchNoResult"):
        """Return employee data for the requested type."""
        employees_data = ConfigReader.load_file(
            "employees", "data", "employee_data.json"
        )
        employee = employees_data.get(employee_type)
        if not employee:
            raise KeyError(f"Employee type '{employee_type}' was not found")
        return employee

    @staticmethod
    def get_leave_data(leave_type="valid_leave"):
        """Return leave data for the requested type."""
        leave_data = ConfigReader.load_file(
            "leave", "data", "leave_data.json"
        )
        data = leave_data.get(leave_type)
        if data is None:
            raise KeyError(f"Leave data type '{leave_type}' was not found")
        return data

    @staticmethod
    def get_my_info_data(data_type="contact"):
        """Return My Info test data for the requested data type."""
        my_info_data = ConfigReader.load_file(
            "my_info", "data", "my_info_data.json"
        )
        data = my_info_data.get(data_type)
        if data is None:
            raise KeyError(f"My Info data type '{data_type}' was not found")
        return data

    # --- Convenience accessors ---

    @staticmethod
    def is_headless():
        return ConfigReader._get_env_bool(
            "ORANGEHRM_HEADLESS",
            ConfigReader.get_config().get("isHeadless", False),
        )

    @staticmethod
    def get_browser():
        return os.getenv(
            "ORANGEHRM_BROWSER",
            ConfigReader.get_config().get("browser", "chrome"),
        )

    @staticmethod
    def get_url():
        return os.getenv(
            "ORANGEHRM_BASE_URL",
            ConfigReader.get_config().get("base_url"),
        )

    @staticmethod
    def get_timeout(timeout_type):
        """Return a configured timeout as a positive number of seconds."""
        timeouts = ConfigReader.get_config().get("timeout", {})
        value = timeouts.get(timeout_type)
        env_name = f"ORANGEHRM_{timeout_type.upper()}_TIMEOUT"
        if os.getenv(env_name) is not None:
            try:
                value = float(os.environ[env_name])
            except ValueError as error:
                raise ValueError(
                    f"Environment variable '{env_name}' must be a number"
                ) from error

        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(
                f"Timeout '{timeout_type}' must be a positive number"
            )
        return value

    @staticmethod
    def _get_env_bool(env_name, default):
        value = os.getenv(env_name)
        if value is None:
            return default

        normalized = value.strip().casefold()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        raise ValueError(
            f"Environment variable '{env_name}' must be a boolean value"
        )

    @staticmethod
    def get_implicit_wait():
        return ConfigReader.get_timeout("implicit_wait")

    @staticmethod
    def get_explicit_wait():
        return ConfigReader.get_timeout("explicit_wait")

    @staticmethod
    def get_test_user_password():
        """Return the password used for dynamically created test users."""
        return os.getenv(
            "ORANGEHRM_TEST_USER_PASSWORD",
            ConfigReader.get_config()
            .get("test_data", {})
            .get("default_user_password"),
        )

    @staticmethod
    def get_user(user_type):
        """Return user data with environment variable overrides applied."""
        user = ConfigReader.get_users().get(user_type)
        if user is None:
            raise KeyError(
                f"User type '{user_type}' was not found in data/users_data.json"
            )

        user_config = dict(user)
        env_prefix = f"ORANGEHRM_{user_type.upper()}"
        user_config["username"] = os.getenv(
            f"{env_prefix}_USERNAME",
            user_config.get("username"),
        )
        user_config["password"] = os.getenv(
            f"{env_prefix}_PASSWORD",
            user_config.get("password"),
        )
        return user_config

    @staticmethod
    def get_username(user_type="admin"):
        return ConfigReader.get_user(user_type).get("username")

    @staticmethod
    def get_password(user_type="admin"):
        return ConfigReader.get_user(user_type).get("password")

    @staticmethod
    def get_leave_employee_name():
        """Return the employee name used for leave entitlements."""
        leave_data = ConfigReader.load_file(
            "leave", "data", "leave_data.json"
        )
        name = leave_data.get("employee_name")
        if not name:
            raise KeyError("'employee_name' was not found in data/leave_data.json")
        return name

    # --- Cache management ---

    @staticmethod
    def reload():
        """Clear the cache so the next call reloads JSON files from disk."""
        ConfigReader._configs.clear()

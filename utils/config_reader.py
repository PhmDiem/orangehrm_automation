import json
import os


class ConfigReader:
    """Đọc và cache các file JSON dùng chung cho framework test."""
    _configs = {}

    # config_reader.py -> utils/ -> project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def load_file(file_key, folder_name, file_name):
        """Đọc 1 file JSON, cache theo file_key. Raise lỗi rõ ràng nếu có vấn đề."""
        if file_key not in ConfigReader._configs:
            file_path = os.path.join(ConfigReader.BASE_DIR, folder_name, file_name)

            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ConfigReader._configs[file_key] = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"File '{file_path}' không đúng format JSON: {e}")

        return ConfigReader._configs[file_key]

    # --- Các hàm lấy dữ liệu cụ thể ---

    @staticmethod
    def get_config():
        return ConfigReader.load_file("config", "config", "config.json")

    @staticmethod
    def get_users():
        """Return users from data/users_data.json."""
        users_data = ConfigReader.load_file("users", "data", "users_data.json")
        return users_data.get("users", {})

    @staticmethod
    def get_employee_name(employee_type="searchExisting"):
        employees_data = ConfigReader.load_file(
            "employees", "data", "employee_data.json"
        )
        employee = employees_data.get(employee_type)
        if not employee:
            raise KeyError(f"Không tìm thấy employee type '{employee_type}'")

        return " ".join(
            value for value in (
                employee.get("firstName"),
                employee.get("middleName"),
                employee.get("lastName"),
            ) if value
        )


    # --- Các hàm tiện ích gọi nhanh ---

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
    def get_user(user_type):
        """Lấy thông tin user theo user_type"""
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
    # --- Tiện ích quản lý cache ---

    @staticmethod
    def reload():
        """Xóa cache để lần gọi tiếp theo đọc lại file JSON từ disk."""
        ConfigReader._configs.clear()
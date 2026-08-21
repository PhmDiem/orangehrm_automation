# OrangeHRM Automation Testing

Dự án Automation Testing cho hệ thống **OrangeHRM** sử dụng Python + Selenium WebDriver.

## Mục tiêu

* Áp dụng **Page Object Model (POM)**
* Tích hợp **PyTest + Allure Report**
* Kiểm tra Database (MySQL)
* Testing API với Auth Token

## Tech Stack

* Python
* Selenium WebDriver
* PyTest + Allure Report
* Page Object Model (POM)
* MySQL (Database verification)
* Requests (API Testing)

## Cấu trúc Project

* `pages/` — Chứa Page Objects
* `tests/` — Chứa test cases
* `data/` — Dữ liệu test (CSV...)
* `utils/` — Helper functions
* `screenshots/` — Ảnh chụp lỗi
* `allure-results/` — Dữ liệu kết quả để tạo báo cáo Allure
* `tests/conftest.py` — Fixtures

## How to Run

```bash
pip install -r requirements.txt

# Chạy test
pytest tests/

# Xem báo cáo
allure serve allure-results
```

## Configuration

Configuration is loaded from `config/config.json` and can be overridden with environment variables:

* `ORANGEHRM_BASE_URL`
* `ORANGEHRM_BROWSER`
* `ORANGEHRM_HEADLESS`
* `ORANGEHRM_ADMIN_USERNAME`
* `ORANGEHRM_ADMIN_PASSWORD`
* `ORANGEHRM_EXPLICIT_WAIT_TIMEOUT`
* `ORANGEHRM_IMPLICIT_WAIT_TIMEOUT`

PowerShell example:

```powershell
$env:ORANGEHRM_ADMIN_USERNAME = "Admin"
$env:ORANGEHRM_ADMIN_PASSWORD = "admin123"

pytest -m login
```

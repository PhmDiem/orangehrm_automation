# OrangeHRM Automation Testing

Dự án Automation Testing cho hệ thống **OrangeHRM** sử dụng Python + Selenium WebDriver.

## Mục tiêu
- Áp dụng **Page Object Model (POM)** 
- Tích hợp **PyTest + Allure Report**
- Kiểm tra Database (MySQL)
- Testing API với Auth Token

## Tech Stack
- Python
- Selenium WebDriver
- PyTest + Allure Report
- Page Object Model (POM)
- MySQL (Database verification)
- Requests (API Testing)

## Cấu trúc Project
- `pages/` — Chứa Page Objects
- `tests/` — Chứa test cases
- `data/` — Dữ liệu test (CSV...)
- `utils/` — Helper functions
- `screenshots/` — Ảnh chụp lỗi
- `reports/` — Báo cáo Allure
- `conftest.py` — Fixtures

## How to Run
```bash
pip install -r requirements.txt

# Chạy test
pytest tests/ --alluredir=reports/allure-results

# Xem báo cáo
allure serve reports/allure-results

# OrangeHRM UI Automation

UI test automation for the public OrangeHRM demo application using Python,
Selenium WebDriver, Pytest, and Allure.

## Scope

The project currently covers browser-based OrangeHRM workflows, including:

- Login and logout
- User management
- Employee management
- Leave types, leave requests, and leave approval/rejection
- Personal information and emergency contacts

The project does not currently contain MySQL/database verification or separate
API test implementations.

## Tech Stack

- Python
- Selenium WebDriver
- Pytest
- Allure Pytest integration
- Page Object Model (POM)

## Project Structure

- `pages/` - Page Object classes
- `tests/` - Test cases and shared fixtures
- `data/` - JSON test data
- `utils/` - Configuration, browser, test data, and reporting helpers
- `config/` - Runtime configuration
- `screenshots/` - Failure screenshots, generated locally
- `allure-results/` - Raw Allure results, generated locally
- `reports/` - Generated Allure reports, generated locally

## Installation and Usage

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Run all tests directly with Pytest:

```bash
pytest tests/
```

Run the provided Windows script to generate and open a timestamped Allure
report. The report is generated for both successful and failed test runs:

```bat
run_tests.bat tests/
```

To open an existing report:

```bat
view_report.bat
```

You can also serve the raw results manually:

```bash
allure serve allure-results
```

## Configuration

Default settings are stored in `config/config.json` and can be overridden with
environment variables:

* `ORANGEHRM_BASE_URL`
* `ORANGEHRM_BROWSER`
* `ORANGEHRM_HEADLESS`
* `ORANGEHRM_ADMIN_USERNAME`
* `ORANGEHRM_ADMIN_PASSWORD`
* `ORANGEHRM_EXPLICIT_WAIT_TIMEOUT`
* `ORANGEHRM_IMPLICIT_WAIT_TIMEOUT`
* `ORANGEHRM_TEST_USER_PASSWORD`
* `ORANGEHRM_SHORT_TIMEOUT`
* `ORANGEHRM_MEDIUM_TIMEOUT`
* `ORANGEHRM_FEEDBACK_TIMEOUT`
* `ORANGEHRM_PAGE_LOAD_TIMEOUT`

PowerShell example:

```powershell
$env:ORANGEHRM_ADMIN_USERNAME = "Admin"
$env:ORANGEHRM_ADMIN_PASSWORD = "admin123"

pytest -m login
```

The public OrangeHRM demo uses the documented demo credentials by default.
For another environment, provide credentials through environment variables
instead of changing the JSON test data.

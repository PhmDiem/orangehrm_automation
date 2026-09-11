@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM =============================================
REM  Usage:
REM  .\run_tests.bat tests/                        -> run all tests
REM  .\run_tests.bat -m login tests/               -> run by marker
REM  .\run_tests.bat -m "login and smoke" tests/  -> run by markers
REM  .\run_tests.bat -k test_login_success tests/  -> run one test
REM  .\run_tests.bat tests/test_login.py           -> run one file
REM  .\run_tests.bat tests/test_login.py::name     -> run one test
REM =============================================

SET RESULTS_DIR=allure-results
SET REPORTS_DIR=reports

FOR /F "tokens=1-5 delims=/ " %%A IN ("%DATE%") DO SET D=%%C-%%B-%%A
FOR /F "tokens=1-2 delims=:." %%A IN ("%TIME: =0%") DO SET T=%%A-%%B
SET TIMESTAMP=%D%_%T%
SET REPORT_DIR=%REPORTS_DIR%\%TIMESTAMP%

echo.
echo [1/4] Removing previous allure-results...
IF EXIST %RESULTS_DIR% rmdir /s /q %RESULTS_DIR%
mkdir %RESULTS_DIR%

echo [2/4] Running pytest %*...
pytest %* --alluredir=%RESULTS_DIR% -v
SET PYTEST_EXIT_CODE=%ERRORLEVEL%
echo.

echo [3/4] Copying history from the previous run...
SET LATEST=
FOR /F "delims=" %%I IN ('dir /b /ad /o-d %REPORTS_DIR% 2^>nul') DO (
    IF NOT DEFINED LATEST SET LATEST=%%I
)
IF DEFINED LATEST (
    IF EXIST %REPORTS_DIR%\%LATEST%\history (
        echo    Found history: %LATEST%
        xcopy /e /i /q %REPORTS_DIR%\%LATEST%\history %RESULTS_DIR%\history
    ) ELSE (
        echo    First run; no history found.
    )
) ELSE (
    echo    No previous report found.
)

echo [4/4] Generating Allure report...
allure generate %RESULTS_DIR% -o %REPORT_DIR% --clean
SET ALLURE_EXIT_CODE=%ERRORLEVEL%
echo.
echo ============================================
echo  DONE! Report saved to: %REPORT_DIR%
echo ============================================
echo.
allure open %REPORT_DIR%

IF NOT "%PYTEST_EXIT_CODE%"=="0" EXIT /b %PYTEST_EXIT_CODE%
EXIT /b %ALLURE_EXIT_CODE%
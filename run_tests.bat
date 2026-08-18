@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM =============================================
REM  Cach dung:
REM  .\run_tests.bat tests/                      → chay tat ca
REM  .\run_tests.bat -m login tests/             → chay theo marker
REM  .\run_tests.bat -m "login and smoke" tests/ → nhieu marker
REM  .\run_tests.bat -k test_login_success tests/→ chay 1 testcase
REM  .\run_tests.bat tests/test_login.py         → chay 1 file
REM  .\run_tests.bat tests/test_login.py::ten_ham→ chay 1 ham
REM =============================================

SET RESULTS_DIR=allure-results
SET REPORTS_DIR=reports

FOR /F "tokens=1-5 delims=/ " %%A IN ("%DATE%") DO SET D=%%C-%%B-%%A
FOR /F "tokens=1-2 delims=:." %%A IN ("%TIME: =0%") DO SET T=%%A-%%B
SET TIMESTAMP=%D%_%T%
SET REPORT_DIR=%REPORTS_DIR%\%TIMESTAMP%

echo.
echo [1/4] Xoa allure-results cu...
IF EXIST %RESULTS_DIR% rmdir /s /q %RESULTS_DIR%
mkdir %RESULTS_DIR%

echo [2/4] Chay pytest %*...
pytest %* --alluredir=%RESULTS_DIR% -v
echo.

echo [3/4] Copy history tu lan chay truoc...
SET LATEST=
FOR /F "delims=" %%I IN ('dir /b /ad /o-d %REPORTS_DIR% 2^>nul') DO (
    IF NOT DEFINED LATEST SET LATEST=%%I
)
IF DEFINED LATEST (
    IF EXIST %REPORTS_DIR%\%LATEST%\history (
        echo    Found history: %LATEST%
        xcopy /e /i /q %REPORTS_DIR%\%LATEST%\history %RESULTS_DIR%\history
    ) ELSE (
        echo    Day la lan chay dau tien, chua co history.
    )
) ELSE (
    echo    Chua co report nao truoc do.
)

echo [4/4] Generate Allure report...
allure generate %RESULTS_DIR% -o %REPORT_DIR% --clean
echo.
echo ============================================
echo  DONE! Report luu tai: %REPORT_DIR%
echo ============================================
echo.
allure open %REPORT_DIR%
@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
echo.
echo ========================================
echo   TEST RUN HISTORY
echo ========================================

REM Check whether the reports directory exists.
IF NOT EXIST reports\ (
    echo   No reports found. Run .\run_tests.bat first.
    pause
    exit /b
)

REM List all reports, newest first.
SET i=0
FOR /F "delims=" %%I IN ('dir /b /ad /o-d reports 2^>nul') DO (
    SET /A i+=1
    SET "folder_!i!=%%I"
    echo   [!i!]  %%I
)

IF %i%==0 (
    echo   No reports found in the reports directory.
    pause
    exit /b
)

echo ========================================
echo   [0]  Exit
echo ========================================
echo.
SET /P choice=Enter a number to open a report:

IF "!choice!"=="0" exit /b
IF "!choice!"=="" exit /b

REM Validate input
IF !choice! GTR %i% (
    echo Invalid choice.
    pause
    exit /b
)

SET SELECTED=!folder_%choice%!
echo.
echo Opening report: reports\!SELECTED!
allure open reports\!SELECTED!
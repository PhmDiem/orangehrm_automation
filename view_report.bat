@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
echo.
echo ========================================
echo   DANH SACH CAC LAN CHAY TEST
echo ========================================

REM Kiem tra thu muc reports co ton tai khong
IF NOT EXIST reports\ (
    echo   Chua co report nao! Hay chay .\run_tests.bat truoc.
    pause
    exit /b
)

REM Liet ke tat ca report, moi nhat len dau
SET i=0
FOR /F "delims=" %%I IN ('dir /b /ad /o-d reports 2^>nul') DO (
    SET /A i+=1
    SET "folder_!i!=%%I"
    echo   [!i!]  %%I
)

IF %i%==0 (
    echo   Khong co report nao trong thu muc reports\
    pause
    exit /b
)

echo ========================================
echo   [0]  Thoat
echo ========================================
echo.
SET /P choice=Chon so de xem report: 

IF "!choice!"=="0" exit /b
IF "!choice!"=="" exit /b

REM Validate input
IF !choice! GTR %i% (
    echo Lua chon khong hop le!
    pause
    exit /b
)

SET SELECTED=!folder_%choice%!
echo.
echo Dang mo report: reports\!SELECTED!
allure open reports\!SELECTED!
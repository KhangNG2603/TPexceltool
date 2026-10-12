@echo off
chcp 65001 >nul
title Cài đặt & Đóng gói Wizard Installer — Thiên Phúc (TPexcel)

echo ============================================================
echo   🛠️  ĐANG TẠO BỘ CÀI ĐẶT WIZARD INSTALLER CHO WINDOWS
echo      Thiên Phúc — Hóa Đơn Bán Hàng ^& Quản Lý Xe
echo ============================================================
echo.

set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
cd /d "%APP_DIR%"

REM 1. Tìm lệnh Python thích hợp
set "PY_CMD="
if exist "%APP_DIR%\.venv\Scripts\python.exe" (
    set "PY_CMD=%APP_DIR%\.venv\Scripts\python.exe"
) else (
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=py -3.11"
    ) else (
        py -3 --version >nul 2>&1
        if not errorlevel 1 (
            set "PY_CMD=py -3"
        ) else (
            python --version >nul 2>&1
            if not errorlevel 1 (
                set "PY_CMD=python"
            )
        )
    )
)

if "%PY_CMD%"=="" (
    echo ❌ KHÔNG TÌM THẤY PYTHON TRÊN MÁY TÍNH!
    echo    Vui lòng cài đặt Python 3.10 trở lên từ https://www.python.org/downloads/
    echo    hoặc từ Microsoft Store, và tích chọn "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [Bước 1/3] Kiểm tra môi trường ảo .venv...
if not exist "%APP_DIR%\.venv\Scripts\python.exe" (
    echo -> Đang tạo môi trường ảo Python .venv...
    %PY_CMD% -m venv "%APP_DIR%\.venv"
    if errorlevel 1 (
        echo ❌ Không thể tạo môi trường ảo .venv.
        pause
        exit /b 1
    )
)

echo [Bước 2/3] Kiểm tra & cài đặt thư viện cần thiết...
"%APP_DIR%\.venv\Scripts\pip.exe" install -r "%APP_DIR%\requirements.txt" --quiet
if errorlevel 1 (
    echo ❌ Có lỗi khi cài đặt thư viện từ requirements.txt.
    pause
    exit /b 1
)
echo -> Đã cài đặt xong thư viện (PySide6, openpyxl, Pillow, PyInstaller).

echo.
echo [Bước 3/3] Đang tiến hành đóng gói Wizard Installer...
"%APP_DIR%\.venv\Scripts\python.exe" "%APP_DIR%\build_windows_installer.py"

echo.
pause

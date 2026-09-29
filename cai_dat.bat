@echo off
chcp 65001 >nul
title Cài đặt - TPexcel (Thiên Phúc Hóa Đơn Bán Hàng)

echo ============================================================
echo   ĐANG TẠO BỘ CÀI ĐẶT DUY NHẤT: TPexcel.exe (Windows)
echo ============================================================

set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

echo [1/2] Đang kiểm tra môi trường Python & cài đặt thư viện...
if not exist "%APP_DIR%\.venv\Scripts\python.exe" (
    python -m venv "%APP_DIR%\.venv"
)
"%APP_DIR%\.venv\Scripts\pip.exe" install --upgrade pip --quiet
"%APP_DIR%\.venv\Scripts\pip.exe" install -r "%APP_DIR%\requirements.txt" --quiet
echo -> Đã cài đặt xong các thư viện cần thiết.

echo [2/2] Đang đóng gói tệp cài đặt duy nhất TPexcel.exe bằng PyInstaller...
"%APP_DIR%\.venv\Scripts\python.exe" "%APP_DIR%\build_windows_installer.py"

echo.
echo ============================================================
echo   ✅ ĐÃ TẠO THÀNH CÔNG BỘ CÀI ĐẶT TPEXCEL.EXE TRÊN WINDOWS!
echo   - Tệp cài đặt duy nhất cho người dùng: dist\TPexcel.exe
echo   - Người dùng chỉ cần tải tệp TPexcel.exe về và nhấp đúp để cài đặt.
echo ============================================================
pause

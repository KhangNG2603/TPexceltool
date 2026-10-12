@echo off
chcp 65001 >nul
title Gỡ cài đặt - Thiên Phúc (TPexcel)

echo ============================================================
echo   🗑️  ĐANG GỠ CÀI ĐẶT: THIÊN PHÚC — HÓA ĐƠN BÁN HÀNG
echo ============================================================
echo.

echo [1/3] Đang xóa Shortcut trên Màn hình chính (Desktop)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Thiên Phúc — Hóa đơn.lnk')) -ErrorAction SilentlyContinue; Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'TPexcel.lnk')) -ErrorAction SilentlyContinue"

echo [2/3] Đang xóa Shortcut trong Menu Start Windows...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'Thiên Phúc')) -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'TPexcel.lnk')) -ErrorAction SilentlyContinue"

echo [3/3] Đang xóa thông tin ứng dụng trong Windows Registry...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\TPexcel" /f >nul 2>&1

echo.
echo ============================================================
echo   ✅ ĐÃ GỠ CÀI ĐẶT THÀNH CÔNG KHỎI WINDOWS!
echo   Các lối tắt và thông tin đăng ký đã được xóa sạch sẽ.
echo ============================================================
pause

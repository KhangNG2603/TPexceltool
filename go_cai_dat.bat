@echo off
chcp 65001 >nul
title Gỡ cài đặt - TPexcel (Thiên Phúc Hóa Đơn Bán Hàng)

echo ============================================================
echo   ĐANG GỠ CÀI ĐẶT: TPexcel (Windows)
echo ============================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'TPexcel.lnk')) -ErrorAction SilentlyContinue"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('StartMenu'), 'Programs', 'TPexcel.lnk')) -ErrorAction SilentlyContinue"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Thiên Phúc - Hóa đơn.lnk')) -ErrorAction SilentlyContinue"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('StartMenu'), 'Programs', 'Thiên Phúc - Hóa đơn.lnk')) -ErrorAction SilentlyContinue"

echo [✓] Đã xóa Shortcut trên Màn hình chính (Desktop) và Menu Start Windows.
echo.
echo ============================================================
echo   ✅ ĐÃ GỠ CÀI ĐẶT THÀNH CÔNG KHỎI WINDOWS!
echo ============================================================
pause

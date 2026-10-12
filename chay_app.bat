@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Thiên Phúc — Hóa đơn bán hàng

if exist dist\TPexcelApp\TPexcelApp.exe (
    start "" "dist\TPexcelApp\TPexcelApp.exe" %*
) else if exist TPexcel.exe (
    start "" "TPexcel.exe" %*
) else (
    set "PY_CMD="
    if exist .venv\Scripts\python.exe (
        set "PY_CMD=.venv\Scripts\python.exe"
    ) else (
        py -3.11 --version >nul 2>&1 && set "PY_CMD=py -3.11"
        if not defined PY_CMD py -3 --version >nul 2>&1 && set "PY_CMD=py -3"
        if not defined PY_CMD python --version >nul 2>&1 && set "PY_CMD=python"
    )
    if not defined PY_CMD (
        echo ❌ Không tìm thấy Python để chạy ứng dụng.
        pause
        exit /b 1
    )
    %PY_CMD% app.py %*
)

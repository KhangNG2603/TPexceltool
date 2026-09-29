@echo off
cd /d "%~dp0"
if exist TPexcel.exe (
    start "" TPexcel.exe
) else if exist dist\TPexcel.exe (
    start "" dist\TPexcel.exe
) else if exist dist\TPexcel\TPexcel.exe (
    start "" dist\TPexcel\TPexcel.exe
) else (
    if not exist .venv\Scripts\python.exe (
        python -m venv .venv
        .venv\Scripts\pip install -r requirements.txt
    )
    .venv\Scripts\python.exe app.py
)

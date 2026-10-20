@echo off
py -3 main.py
if errorlevel 1 (
    echo.
    echo Could not start Focus Desk.
    echo Install Python 3 from https://www.python.org/downloads/ and try again.
    pause
)

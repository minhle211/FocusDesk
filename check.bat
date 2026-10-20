@echo off
py -3 -m unittest discover -s tests -t . -v
echo.
pause

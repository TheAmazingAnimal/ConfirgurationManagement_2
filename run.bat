@echo off
cd /d "%~dp0"
set PYTHONPATH=src
if "%1"=="test" (
    python -m unittest discover -s tests -v
) else (
    python src\main.py %*
)

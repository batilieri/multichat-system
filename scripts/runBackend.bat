@echo off
REM ========================================
REM  MultiChat System - Iniciar apenas o Backend
REM ========================================
cd multichat_system
venv_windows\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
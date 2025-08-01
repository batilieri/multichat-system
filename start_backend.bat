@echo off
REM Iniciar Backend Django com ambiente virtual
cd multichat_system
if exist "..\venv_windows_new\Scripts\activate.bat" (
    call ..\venv_windows_new\Scripts\activate.bat
) else if exist "..\venv_windows\Scripts\activate.bat" (
    call ..\venv_windows\Scripts\activate.bat
)
python manage.py runserver 8000
pause 
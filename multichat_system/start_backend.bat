@echo off
setlocal

echo ========================================
echo    MultiChat System - Backend
set VENV_PATH=venv_windows\Scripts\activate.bat
echo ========================================
echo.

cd multichat_system

if not exist "%VENV_PATH%" (
    echo Ambiente virtual nao encontrado. Criando ambiente virtual...
    python -m venv venv_windows
    if errorlevel 1 (
        echo ERRO ao criar ambiente virtual. Verifique o Python instalado.
        exit /b 1
    )
)

echo Ativando ambiente virtual...
call %VENV_PATH%
if errorlevel 1 (
    echo ERRO ao ativar ambiente virtual.
    exit /b 1
)

echo.
echo Verificando dependencias...
python -c "import django; print('Django OK')" 2>nul || (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

if errorlevel 1 (
    echo ERRO ao instalar dependencias.
    exit /b 1
)

echo.
echo Executando migracoes...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERRO nas migracoes do banco de dados.
    exit /b 1
)

echo.
echo Iniciando servidor...
echo Backend disponivel em: http://localhost:8000
echo Admin disponivel em: http://localhost:8000/admin
echo.
python manage.py runserver 0.0.0.0:8000

endlocal 
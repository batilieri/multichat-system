@echo off
title MultiChat - Iniciar Todos os Servidores
echo ========================================
echo    MULTICHAT - TODOS OS SERVIDORES
echo ========================================
echo.
echo Iniciando backend Django e servidor webhook...
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0multichat_system"

REM Verificar se o ambiente virtual existe
if exist "venv_windows\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv_windows\Scripts\activate.bat
) else (
    echo Ambiente virtual nao encontrado. Tentando usar Python global...
)

REM Verificar se o Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Certifique-se de que o Python esta instalado e no PATH
    pause
    exit /b 1
)

echo.
echo Verificando dependencias...
python -c "import flask, pyngrok" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias do webhook...
    pip install -r requirements_webhook.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo    INICIANDO SERVIDORES
echo ========================================
echo.
echo Os servidores serao iniciados em janelas separadas:
echo - Backend Django: http://localhost:8000
echo - Webhook Server: http://localhost:5000
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM Iniciar o servidor Django em uma nova janela
echo Iniciando servidor Django...
start "MultiChat Django Server" cmd /k "cd /d "%~dp0multichat_system" && python manage.py runserver"

REM Aguardar um pouco para o Django inicializar
timeout /t 3 /nobreak >nul

REM Iniciar o servidor webhook em outra janela
echo Iniciando servidor webhook...
start "MultiChat Webhook Server" cmd /k "cd /d "%~dp0multichat_system" && python webhook\servidor_webhook_local.py"

echo.
echo ========================================
echo    SERVIDORES INICIADOS!
echo ========================================
echo.
echo Backend Django: http://localhost:8000
echo Webhook Server: http://localhost:5000
echo.
echo Para parar os servidores, feche as janelas correspondentes
echo ou pressione Ctrl+C em cada janela
echo.
echo Pressione qualquer tecla para sair...
pause 
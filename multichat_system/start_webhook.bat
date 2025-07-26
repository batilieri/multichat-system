@echo off
title MultiChat Webhook Server
echo ========================================
echo    MULTICHAT WEBHOOK SERVER
echo ========================================
echo.
echo Iniciando servidor webhook...
echo.

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
echo    INICIANDO SERVIDOR WEBHOOK
echo ========================================
echo.
echo O servidor webhook sera iniciado em uma nova janela
echo URL local: http://localhost:5000
echo URL publica sera mostrada na janela do webhook
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM Iniciar o servidor webhook em uma nova janela
start "MultiChat Webhook Server" cmd /k "python webhook\servidor_webhook_local.py"

echo.
echo Servidor webhook iniciado em nova janela!
echo.
echo Para parar o servidor, feche a janela do webhook
echo ou pressione Ctrl+C na janela do webhook
echo.
pause 
@echo off
chcp 65001 >nul
title Teste Webhook Simples
echo ========================================
echo    TESTE WEBHOOK SIMPLES
echo ========================================
echo.
echo Testando execucao basica...
echo.

REM Obter o diretório atual do script
set "SCRIPT_DIR=%~dp0"
echo Diretorio do script: %SCRIPT_DIR%

REM Navegar para o diretório do projeto
cd /d "%SCRIPT_DIR%multichat_system"
echo Diretorio atual: %CD%

echo.
echo Verificando se o arquivo existe...
if exist "webhook\servidor_webhook_local.py" (
    echo ✅ Arquivo encontrado: webhook\servidor_webhook_local.py
) else (
    echo ❌ Arquivo nao encontrado: webhook\servidor_webhook_local.py
    pause
    exit /b 1
)

echo.
echo Verificando Python...
python --version
if errorlevel 1 (
    echo ❌ Python nao encontrado via 'python'
    py --version
    if errorlevel 1 (
        echo ❌ Python nao encontrado via 'py'
        pause
        exit /b 1
    ) else (
        echo ✅ Python encontrado via 'py'
        set PYTHON_CMD=py
    )
) else (
    echo ✅ Python encontrado via 'python'
    set PYTHON_CMD=python
)

echo.
echo Testando execucao do servidor...
echo Comando: %PYTHON_CMD% webhook\servidor_webhook_local.py
echo.
echo Pressione qualquer tecla para executar...
pause >nul

REM Executar diretamente (sem nova janela)
%PYTHON_CMD% webhook\servidor_webhook_local.py

echo.
echo Teste concluido!
pause 
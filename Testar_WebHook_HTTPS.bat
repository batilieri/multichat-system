@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    TESTE WEBHOOK HTTPS - MULTICHAT
echo ========================================
echo.
echo 🔒 Testando configuração HTTPS...
echo 🌐 Verificando túnel ngrok...
echo 📱 Validando webhook...
echo.
echo ========================================
echo.

:: Verificar se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo 💡 Instale o Python em: https://python.org
    pause
    exit /b 1
)

:: Navegar para o diretório do projeto
cd /d "%~dp0"

:: Verificar se o ambiente virtual existe
if not exist "multichat_system\venv_windows_new\Scripts\activate.bat" (
    echo ❌ ERRO: Ambiente virtual não encontrado!
    echo 💡 Execute primeiro: setup_system.py
    pause
    exit /b 1
)

:: Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call multichat_system\venv_windows_new\Scripts\activate.bat

:: Verificar dependências
echo 📦 Verificando dependências...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo ❌ Requests não encontrado!
    echo 💡 Instalando requests...
    pip install requests
)

:: Executar teste
echo.
echo ========================================
echo 🚀 EXECUTANDO TESTE HTTPS
echo ========================================
echo.

python testar_webhook_https.py

echo.
echo ========================================
echo ✅ TESTE CONCLUÍDO!
echo ========================================
echo.
echo 💡 Verifique os resultados acima
echo 🔒 Se HTTPS está funcionando, configure no WhatsApp
echo 📱 Use a URL HTTPS fornecida pelo ngrok
echo.
pause 
@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    MULTICHAT WEBHOOK SERVER - HTTPS
echo ========================================
echo.
echo 🚀 Iniciando servidor webhook com HTTPS...
echo 🔒 Configuração: Protocolo HTTPS forçado
echo 🌐 Ngrok: Túnel HTTPS público
echo 📱 WhatsApp: Webhook seguro
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
cd /d "%~dp0multichat_system"

:: Verificar se o ambiente virtual existe
if not exist "venv_windows_new\Scripts\activate.bat" (
    echo ❌ ERRO: Ambiente virtual não encontrado!
    echo 💡 Execute primeiro: setup_system.py
    pause
    exit /b 1
)

:: Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv_windows_new\Scripts\activate.bat

:: Verificar dependências
echo 📦 Verificando dependências...
python -c "import flask, pyngrok" 2>nul
if errorlevel 1 (
    echo ❌ Dependências faltando!
    echo 💡 Instalando dependências...
    pip install flask pyngrok requests
)

:: Verificar Django
echo 🐍 Verificando Django...
python -c "import django" 2>nul
if errorlevel 1 (
    echo ❌ Django não encontrado!
    echo 💡 Execute: pip install django
    pause
    exit /b 1
)

:: Executar migrações se necessário
echo 🔄 Verificando migrações...
python manage.py makemigrations --dry-run >nul 2>&1
if not errorlevel 1 (
    echo 📝 Aplicando migrações...
    python manage.py migrate --verbosity=0
)

:: Iniciar servidor webhook
echo.
echo ========================================
echo 🚀 INICIANDO SERVIDOR WEBHOOK HTTPS
echo ========================================
echo.
echo 📱 Aguardando conexões...
echo 🔒 Protocolo: HTTPS
echo 🌐 Ngrok: Túnel público
echo 📊 Logs: Console
echo.
echo 💡 Para parar: Ctrl+C
echo ========================================
echo.

:: Executar servidor webhook
python webhook/servidor_webhook_local.py

:: Se chegou aqui, houve erro
echo.
echo ❌ Servidor webhook parou inesperadamente!
echo 💡 Verifique os logs acima
pause 
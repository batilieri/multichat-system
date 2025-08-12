#!/usr/bin/env fish

echo "========================================"
echo "   MULTICHAT WEBHOOK SERVER"
echo "========================================"
echo
echo "Iniciando servidor webhook..."
echo

# Verificar se o ambiente virtual existe
if test -f "venv_windows/Scripts/activate.fish"
    echo "Ativando ambiente virtual..."
    source venv_windows/Scripts/activate.fish
else if test -f "venv/bin/activate.fish"
    echo "Ativando ambiente virtual..."
    source venv/bin/activate.fish
else
    echo "Ambiente virtual não encontrado. Tentando usar Python global..."
end

# Verificar se o Python está disponível
if not command -q python
    echo "ERRO: Python não encontrado!"
    echo "Certifique-se de que o Python está instalado e no PATH"
    read -P "Pressione Enter para sair..."
    exit 1
end

echo
echo "Verificando dependências..."
python -c "import flask, pyngrok" ^/dev/null
if test $status -ne 0
    echo "Instalando dependências do webhook..."
    pip install -r requirements_webhook.txt
    if test $status -ne 0
        echo "ERRO: Falha ao instalar dependências!"
        read -P "Pressione Enter para sair..."
        exit 1
    end
end

echo
echo "========================================"
echo "   INICIANDO SERVIDOR WEBHOOK"
echo "========================================"
echo
echo "O servidor webhook será iniciado em uma nova janela"
echo "URL local: http://localhost:5000"
echo "URL pública será mostrada na janela do webhook"
echo
read -P "Pressione Enter para continuar..."

# Iniciar o servidor webhook (nova aba/terminal)
if command -q gnome-terminal
    gnome-terminal -- bash -c "python webhook/servidor_webhook_local.py; exec bash"
else if command -q xterm
    kitty -e "python webhook/servidor_webhook_local.py"
else
    echo "Iniciando no terminal atual..."
    python webhook/servidor_webhook_local.py
end

echo
echo "Servidor webhook iniciado!"
echo "Para parar o servidor, feche a janela ou pressione Ctrl+C"
echo
read -P "Pressione Enter para sair..."

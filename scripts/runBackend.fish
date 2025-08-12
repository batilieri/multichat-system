#!/bin/bash

# Script para executar o backend Django
cd multichat_system

# Verificar se existe ambiente virtual
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python -m venv venv
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Executar o servidor Django
echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000 
#!/usr/bin/env fish

# Script para executar o frontend React (Fish Shell)
cd multichat-frontend

# Verificar se node_modules existe
if not test -d "node_modules"
    echo "Instalando dependências..."
    # Usar --legacy-peer-deps para resolver conflitos
    npm install --legacy-peer-deps
else
    echo "Dependências já instaladas."
end

# Verificar se vite está instalado
if not command -q vite
    echo "Instalando vite..."
    npm install -g vite
end

# Executar o servidor de desenvolvimento
echo "Iniciando servidor de desenvolvimento..."
npm run dev 
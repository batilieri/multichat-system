# 🚀 Comandos para Iniciar o MultiChat System

Este documento contém todas as opções para iniciar os servidores do MultiChat System.

## 📁 Arquivos .bat Criados

### 1. `start_backend_complete.bat` - Servidor Backend Completo
**Funcionalidades:**
- ✅ Verifica estrutura do projeto
- ✅ Cria ambiente virtual se necessário
- ✅ Ativa ambiente virtual automaticamente
- ✅ Instala dependências Python
- ✅ Executa migrações do banco
- ✅ Cria superusuário padrão
- ✅ Executa dados de teste
- ✅ Inicia servidor Django

**Como usar:**
```bash
# Execute na pasta raiz do projeto
start_backend_complete.bat
```

### 2. `start_frontend_complete.bat` - Servidor Frontend Completo
**Funcionalidades:**
- ✅ Verifica estrutura do projeto
- ✅ Verifica instalação do Node.js
- ✅ Instala dependências npm
- ✅ Cria arquivo .env se necessário
- ✅ Inicia servidor Vite

**Como usar:**
```bash
# Execute na pasta raiz do projeto
start_frontend_complete.bat
```

### 3. `start_both_servers.bat` - Ambos Servidores Simultaneamente
**Funcionalidades:**
- ✅ Abre duas janelas separadas
- ✅ Inicia backend primeiro
- ✅ Aguarda inicialização
- ✅ Inicia frontend
- ✅ Mostra todas as URLs

**Como usar:**
```bash
# Execute na pasta raiz do projeto
start_both_servers.bat
```

## 🎯 Opções de Inicialização

### **Opção 1: Iniciar Ambos (Recomendado)**
```bash
start_both_servers.bat
```
- Abre duas janelas automaticamente
- Backend na porta 8000
- Frontend na porta 5173

### **Opção 2: Iniciar Separadamente**
```bash
# Terminal 1 - Backend
start_backend_complete.bat

# Terminal 2 - Frontend (após backend estar rodando)
start_frontend_complete.bat
```

### **Opção 3: Comandos Manuais**
```bash
# Backend
cd multichat_system
venv_windows\Scripts\activate.bat
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Frontend (novo terminal)
cd multichat-frontend
npm install
npm run dev
```

## 🌐 URLs de Acesso

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | http://localhost:5173 | Interface principal |
| **Backend API** | http://localhost:8000 | API REST |
| **Admin Django** | http://localhost:8000/admin | Painel administrativo |

## 👤 Credenciais Padrão

- **Email:** admin@multichat.com
- **Senha:** admin123

## ⚠️ Pré-requisitos

### Para o Backend:
- ✅ Python 3.8+ instalado
- ✅ pip disponível

### Para o Frontend:
- ✅ Node.js 16+ instalado
- ✅ npm disponível

## 🔧 Solução de Problemas

### Erro: "Python não encontrado"
```bash
# Verifique se o Python está no PATH
python --version
```

### Erro: "Node.js não encontrado"
```bash
# Baixe e instale do site oficial
# https://nodejs.org/
```

### Erro: "Porta já em uso"
```bash
# Verifique se não há outros serviços rodando
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### Erro: "Dependências não instaladas"
```bash
# Backend
cd multichat_system
pip install -r requirements.txt

# Frontend
cd multichat-frontend
npm install
```

## 📝 Logs e Debug

### Backend Logs:
- Erros aparecem na janela do backend
- Logs do Django são exibidos em tempo real

### Frontend Logs:
- Erros aparecem na janela do frontend
- Logs do Vite são exibidos em tempo real

## 🛑 Como Parar os Servidores

### Se usar `start_both_servers.bat`:
- Feche as janelas dos terminais
- Ou pressione `Ctrl+C` em cada janela

### Se usar comandos manuais:
- Pressione `Ctrl+C` no terminal

## 💡 Dicas Importantes

1. **Sempre execute o backend primeiro**
2. **Mantenha as janelas dos terminais abertas**
3. **Verifique se as portas estão livres**
4. **Use os arquivos .bat para facilitar o processo**
5. **Em caso de erro, verifique os logs nas janelas**

## 🔄 Atualizações

Para atualizar o projeto:
```bash
# Backend
cd multichat_system
git pull
pip install -r requirements.txt
python manage.py migrate

# Frontend
cd multichat-frontend
git pull
npm install
``` 
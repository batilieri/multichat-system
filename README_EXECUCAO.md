# 🚀 MultiChat System - Guia de Execução

## 📋 Visão Geral

O MultiChat System é uma plataforma completa para atendimento via WhatsApp com:
- **Backend Django** com API REST
- **Frontend React** com interface moderna
- **Integração W-APi** para WhatsApp
- **Sistema de webhooks** para receber mensagens

## 🎯 Execução Rápida

### Opção 1: Scripts Automáticos (Recomendado)

#### Backend
```bash
cd multichat_system
start_backend.bat
```

#### Frontend
```bash
cd multichat-frontend
start_frontend.bat
```

### Opção 2: Comandos Manuais

#### Backend
```bash
cd multichat_system
venv_windows\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

#### Frontend
```bash
cd multichat-frontend
npm run dev
```

## 🌐 URLs de Acesso

- **Backend API:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin
- **Frontend:** http://localhost:5173

## 🔑 Credenciais

- **Email:** admin@multichat.com
- **Senha:** admin123

## 📁 Estrutura do Projeto

```
whatsapp/
├── multichat_system/          # Backend Django
│   ├── api/                   # API REST
│   ├── authentication/        # Autenticação
│   ├── core/                  # Modelos principais
│   ├── webhook/               # Webhooks
│   ├── manage.py
│   ├── requirements.txt
│   └── start_backend.bat      # Script de execução
├── multichat-frontend/        # Frontend React
│   ├── src/
│   ├── package.json
│   └── start_frontend.bat     # Script de execução
└── README_EXECUCAO.md         # Este arquivo
```

## 🔧 Configuração Inicial (Primeira vez)

### 1. Backend Django

```bash
cd multichat_system

# Ativar ambiente virtual
venv_windows\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Executar configuração automática
python run_dev.py
```

### 2. Frontend React

```bash
cd multichat-frontend

# Instalar dependências
npm install
```

## 🚀 Execução Diária

### Terminal 1 - Backend
```bash
cd multichat_system
venv_windows\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

### Terminal 2 - Frontend
```bash
cd multichat-frontend
npm run dev
```

## 📊 Funcionalidades Principais

### ✅ Gestão de Clientes
- Cadastro e gerenciamento de clientes
- Associação de usuários a clientes
- Configuração de departamentos

### ✅ Integração WhatsApp
- Conexão com instâncias W-APi
- Geração de QR Codes
- Envio de mensagens
- Recebimento via webhooks

### ✅ Sistema de Chat
- Interface de atendimento
- Histórico de conversas
- Status de mensagens

### ✅ Dashboard
- Estatísticas em tempo real
- Monitoramento de instâncias
- Relatórios de atividade

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Porta em Uso
```bash
# Usar porta diferente
python manage.py runserver 0.0.0.0:8001
```

#### 2. Erro de Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

#### 3. Erro de Migrações
```bash
# Resetar migrações
python manage.py makemigrations
python manage.py migrate
```

#### 4. Erro de CORS
- Verificar se backend está na porta 8000
- Verificar configurações no settings.py

### Logs do Sistema

Os logs estão em:
- `multichat_system/logs/django.log`

## 🌐 Configuração W-APi

### Credenciais de Teste
- **Instância:** 3B6XIW-ZTS923-GEAY6V
- **Token:** **************************

### Webhook URL
```
http://localhost:8000/webhook/
```

## 📝 Comandos Úteis

### Backend
```bash
# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Coletar estáticos
python manage.py collectstatic

# Criar dados de teste
python create_test_data.py
```

### Frontend
```bash
# Build produção
npm run build

# Preview build
npm run preview

# Lint código
npm run lint
```

## 🎯 Próximos Passos

1. **Testar API:** Acesse http://localhost:8000
2. **Acessar Admin:** http://localhost:8000/admin
3. **Testar Frontend:** http://localhost:5173
4. **Conectar W-APi:** Use credenciais de teste
5. **Enviar Mensagens:** Teste via interface

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `multichat_system/logs/`
2. Teste endpoints individualmente
3. Verifique configurações de ambiente

---

**Status:** ✅ Pronto para desenvolvimento  
**Versão:** 1.0.0  
**Data:** 2025-07-11 

---

## 1. Crie um repositório no GitHub

1. Acesse [https://github.com](https://github.com)
2. Clique em **New repository** (Novo repositório)
3. Dê um nome para o repositório (ex: `multichat-system`)
4. (Opcional) Adicione uma descrição
5. Marque como **Private** (privado) ou **Public** (público), conforme desejar
6. Clique em **Create repository**

---

## 2. Inicialize o Git no seu projeto (caso ainda não tenha)

Abra o terminal/prompt de comando na pasta raiz do seu projeto (onde está a pasta `multichat_system` e `multichat-frontend`):

```bash
git init
```

---

## 3. Adicione os arquivos para versionamento

```bash
git add .
```

---

## 4. Faça o primeiro commit

```bash
git commit -m "Primeiro commit do projeto MultiChat"
```

---

## 5. Conecte ao repositório do GitHub

No GitHub, após criar o repositório, ele vai mostrar um endereço parecido com:
```
https://github.com/seu-usuario/multichat-system.git
```
No terminal, rode:

```bash
git remote add origin https://github.com/seu-usuario/multichat-system.git
```
(Substitua pelo endereço do seu repositório!)

---

## 6. Envie o projeto para o GitHub

```bash
git branch -M main
git push -u origin main
```

---

## 7. Pronto!

Agora seu projeto está no GitHub!  
Sempre que fizer alterações, use:

```bash
git add .
git commit -m "Descreva sua alteração"
git push
```

---

## ⚠️ Dicas importantes

- **Nunca envie arquivos sensíveis** (senhas, .env com dados reais, etc).  
  Adicione esses arquivos ao `.gitignore` antes de dar o `git add .`.
- O arquivo `.gitignore` já deve conter:  
  ```
  venv/
  venv_windows/
  *.pyc
  __pycache__/
  db.sqlite3
  *.env
  ```
  (Se não tiver, posso criar para você!)

---

Se quiser, posso criar o `.gitignore` ideal para seu projeto.  
Se tiver dúvidas em algum passo, me envie o erro ou print que te ajudo! 

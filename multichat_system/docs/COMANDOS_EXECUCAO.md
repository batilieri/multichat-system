# 🚀 Comandos para Executar o MultiChat System

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 20+
- npm ou pnpm

## 🔧 Configuração Inicial (Primeira vez)

### 1. Configurar Backend Django

```bash
# Navegar para o diretório do backend
cd multichat_system

# Ativar ambiente virtual (Windows)
venv_windows\Scripts\Activate.ps1

# OU ativar ambiente virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Executar script de configuração automática
python run_dev.py
```

### 2. Configurar Frontend React

```bash
# Navegar para o diretório do frontend
cd ../multichat-frontend

# Instalar dependências
npm install
# OU
pnpm install
```

## 🚀 Execução Diária

### Backend (Terminal 1)

```bash
cd multichat_system
venv_windows\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

**URLs do Backend:**
- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- Documentação: http://localhost:8000/api/docs/

### Frontend (Terminal 2)

```bash
cd multichat-frontend
npm run dev
# OU
pnpm dev
```

**URL do Frontend:** http://localhost:5173

## 🔑 Credenciais de Acesso

### Superusuário (Admin)
- **Email:** admin@multichat.com
- **Senha:** admin123

### Dados de Teste
O sistema já vem com dados de teste pré-configurados:
- Clientes de exemplo
- Departamentos
- Instâncias W-APi de teste

## 🛠️ Comandos Úteis

### Backend

```bash
# Criar superusuário manualmente
python manage.py createsuperuser

# Executar migrações
python manage.py makemigrations
python manage.py migrate

# Criar dados de teste
python create_test_data.py

# Shell do Django
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic
```

### Frontend

```bash
# Build para produção
npm run build

# Preview do build
npm run preview

# Lint do código
npm run lint
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Migrações
```bash
# Resetar migrações
rm -rf */migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

#### 2. Erro de Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

#### 3. Erro de Porta em Uso
```bash
# Usar porta diferente
python manage.py runserver 0.0.0.0:8001
```

#### 4. Erro de CORS
- Verificar se o backend está rodando na porta 8000
- Verificar configurações CORS no settings.py

## 📊 Endpoints da API

### Autenticação
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token

### Clientes
- `GET /api/clientes/` - Listar clientes
- `POST /api/clientes/` - Criar cliente
- `GET /api/clientes/{id}/` - Detalhes do cliente
- `POST /api/clientes/{id}/connect_wapi/` - Conectar W-APi

### WhatsApp
- `GET /api/whatsapp-instances/` - Listar instâncias
- `POST /api/whatsapp-instances/{id}/refresh_status/` - Atualizar status
- `POST /api/whatsapp-instances/{id}/send_message/` - Enviar mensagem

### Webhook
- `POST /webhook/` - Endpoint para receber webhooks
- `GET /webhook/status/` - Status do webhook

## 🌐 Configuração W-APi

### Credenciais de Teste
- **Instância:** 3B6XIW-ZTS923-GEAY6V
- **Token:** Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF

### Webhook URL
Configure na W-APi:
```
http://localhost:8000/webhook/
```

## 📝 Logs

Os logs do sistema estão em:
- `multichat_system/logs/django.log`

## 🎯 Próximos Passos

1. **Testar API:** Acesse http://localhost:8000 para ver os endpoints
2. **Acessar Admin:** http://localhost:8000/admin
3. **Testar Frontend:** http://localhost:5173
4. **Conectar W-APi:** Use as credenciais de teste
5. **Enviar Mensagens:** Teste o envio via API

---

**Status:** ✅ Pronto para desenvolvimento  
**Versão:** 1.0.0  
**Data:** 2025-05-11 
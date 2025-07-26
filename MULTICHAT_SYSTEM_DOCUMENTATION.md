# 🚀 MultiChat System - Sistema SaaS Completo

## 📋 Visão Geral

O **MultiChat System** é um sistema SaaS completo para atendimento via WhatsApp, desenvolvido com **Django** (backend) e **React** (frontend). O sistema oferece uma solução robusta para empresas que desejam centralizar e gerenciar seus atendimentos via WhatsApp de forma profissional.

## 🌐 URLs de Acesso

### Sistema Deployado (Produção)
- **Frontend**: https://sqamvuir.manus.space
- **Backend API**: https://8000-i1wpa1lpumqnroznpgkss-d2b2d050.manusvm.computer

### Credenciais de Teste
- **Email**: admin@multichat.com
- **Senha**: admin123

**OU**

- **Email**: colaborador@multichat.com  
- **Senha**: 123456

## 🏗️ Arquitetura do Sistema

### Backend (Django)
- **Framework**: Django 4.2.15 + Django REST Framework
- **Banco de Dados**: SQLite (desenvolvimento) / MySQL (produção)
- **Autenticação**: JWT (JSON Web Tokens)
- **APIs**: RESTful com documentação automática

### Frontend (React)
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS + Shadcn/UI
- **Animações**: Framer Motion
- **Ícones**: Lucide React
- **Estado**: Context API

## 📁 Estrutura do Projeto

```
multichat_system/
├── multichat/                 # Configurações Django
├── core/                      # Models principais
├── api/                       # APIs REST
├── authentication/            # Sistema de autenticação
├── webhook/                   # Sistema de webhooks
├── static/                    # Arquivos estáticos
├── venv_windows/              # Ambiente virtual para Windows
├── start_backend.bat          # Script para iniciar backend (Windows)
├── start_webhook.bat          # Script para iniciar webhook (Windows)
├── runBackend.bat             # Script alternativo para backend (Windows)
└── manage.py

multichat-frontend/
├── src/
│   ├── components/           # Componentes React
│   ├── contexts/            # Contextos (Auth, Theme)
│   └── App.jsx              # Aplicação principal
├── start_frontend.bat        # Script para iniciar frontend (Windows)
├── dist/                    # Build de produção
└── vite.config.js
```

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

1. **Cliente** - Empresas que usam o sistema
2. **Usuario** - Usuários do sistema (master/colaborador)
3. **Departamento** - Departamentos das empresas
4. **Chat** - Conversas do WhatsApp
5. **Mensagem** - Mensagens das conversas
6. **Atribuicao** - Atribuição de chats para usuários
7. **WhatsappInstance** - Instâncias do WhatsApp
8. **Sender** - Remetentes das mensagens

## 🔧 Funcionalidades Implementadas

### ✅ Backend (Django)
- [x] Sistema de autenticação JWT
- [x] APIs REST completas para todas as entidades
- [x] Sistema de permissões por tipo de usuário
- [x] Webhook para receber dados do WhatsApp
- [x] Processamento de mensagens
- [x] Sistema de atribuição de chats
- [x] Filtros e paginação nas APIs
- [x] Documentação automática da API

### ✅ Frontend (React)
- [x] Tela de login responsiva
- [x] Dashboard com métricas (com dados mock)
- [x] Lista de chats com filtros
- [x] Interface de chat em tempo real
- [x] Gestão de usuários
- [x] Configurações do sistema
- [x] Tema claro/escuro
- [x] Design responsivo
- [x] Animações suaves

## 🚀 Como Executar Localmente

### Windows (recomendado)

#### 1. Backend (Django)

Execute o script para iniciar o backend:

```bat
runBackend.bat
```

Ou, alternativamente:

```bat
multichat_system\start_backend.bat
```

#### 2. Webhook

Execute o script para iniciar o servidor webhook:

```bat
multichat_system\start_webhook.bat
```

#### 3. Frontend (React)

Execute o script para iniciar o frontend:

```bat
frontend.bat
```

Ou, dentro da pasta do frontend:

```bat
multichat-frontend\start_frontend.bat
```

> **Observação:** Os scripts .bat já cuidam da ativação do ambiente virtual (quando necessário) e instalação de dependências.

### Linux/Mac (alternativo)

```bash
cd multichat_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python create_test_data.py
python manage.py runserver 0.0.0.0:8000
```

```bash
cd multichat-frontend
npm install --legacy-peer-deps
npm run dev
```

## 📡 APIs Disponíveis

### Autenticação
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token
- `GET /api/auth/verify/` - Verificar token
- `POST /api/auth/register/` - Registro

### Recursos Principais
- `GET /api/clientes/` - Listar clientes
- `GET /api/usuarios/` - Listar usuários
- `GET /api/chats/` - Listar chats
- `GET /api/mensagens/` - Listar mensagens
- `GET /api/departamentos/` - Listar departamentos

### Webhook
- `POST /webhook/whatsapp/` - Receber dados do WhatsApp

## 🔐 Sistema de Permissões

### Tipos de Usuário
1. **Master** - Acesso total ao sistema
2. **Colaborador** - Acesso limitado aos chats atribuídos

### Controle de Acesso
- Autenticação JWT obrigatória
- Filtros automáticos por cliente
- Permissões baseadas no tipo de usuário

## 🎨 Interface do Usuário

### Características
- **Design Moderno**: Interface limpa e profissional
- **Responsivo**: Funciona em desktop e mobile
- **Tema Escuro/Claro**: Alternância automática
- **Animações**: Transições suaves com Framer Motion
- **Acessibilidade**: Componentes acessíveis

### Páginas Principais
1. **Login** - Autenticação de usuários
2. **Dashboard** - Visão geral com métricas
3. **Chats** - Lista e visualização de conversas
4. **Usuários** - Gestão da equipe
5. **Configurações** - Configurações do sistema

## 🔄 Sistema de Webhook

### Funcionalidades
- Recepção de mensagens do WhatsApp
- Processamento automático de dados
- Criação de chats e mensagens
- Sistema de atribuição automática

### Endpoints
- Verificação de webhook
- Processamento de mensagens
- Logs de eventos

## 📊 Dados de Teste

O sistema inclui dados de teste pré-configurados:

### Cliente
- **Empresa**: Empresa Teste Ltda
- **CNPJ**: 12.345.678/0001-90
- **Plano**: Básico

### Usuários
- **Admin**: admin@multichat.com (master)
- **Colaborador**: colaborador@multichat.com (colaborador)

### Chats Mock
- João Silva (aguardando)
- Ana Costa (resolvido)
- Suporte Técnico (em andamento)

## 🛠️ Tecnologias Utilizadas

### Backend
- Django 4.2.15
- Django REST Framework 3.14.0
- Django CORS Headers
- Django Filter
- Python Decouple
- Rich (terminal colorido)

### Frontend
- React 18
- Vite 6
- Tailwind CSS
- Shadcn/UI
- Framer Motion
- Lucide React
- Context API

### Deploy
- Frontend: Manus Space (https://sqamvuir.manus.space)
- Backend: Manus VM (porta exposta)

## 📈 Próximos Passos

### Funcionalidades Futuras
1. **Chat em Tempo Real** - WebSockets para mensagens instantâneas
2. **Notificações Push** - Alertas em tempo real
3. **Relatórios Avançados** - Analytics detalhados
4. **Integração WhatsApp Business** - API oficial
5. **Sistema de Tickets** - Gestão de suporte
6. **Chatbots** - Respostas automáticas
7. **Métricas Avançadas** - Dashboard com dados reais

### Melhorias Técnicas
1. **Testes Automatizados** - Unit e integration tests
2. **CI/CD Pipeline** - Deploy automático
3. **Monitoramento** - Logs e métricas
4. **Cache** - Redis para performance
5. **CDN** - Otimização de assets

## 🎯 Conclusão

O **MultiChat System** é uma solução completa e moderna para atendimento via WhatsApp, oferecendo:

- ✅ **Backend robusto** com Django e APIs REST
- ✅ **Frontend moderno** com React e design responsivo
- ✅ **Sistema de autenticação** seguro com JWT
- ✅ **Interface intuitiva** para gestão de atendimentos
- ✅ **Arquitetura escalável** para crescimento futuro
- ✅ **Deploy funcional** em produção

O sistema está pronto para uso e pode ser facilmente expandido com novas funcionalidades conforme a necessidade do negócio.

---

**Desenvolvido com ❤️ usando Django + React**


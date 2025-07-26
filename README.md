# MultiChat System

Sistema completo de gerenciamento de múltiplas instâncias do WhatsApp com interface web moderna.

## 🚀 Funcionalidades

- **Múltiplas Instâncias**: Gerencie várias instâncias do WhatsApp simultaneamente
- **Interface Web Moderna**: Frontend React com design responsivo
- **Sistema de Webhooks**: Recebimento automático de mensagens
- **Download de Mídias**: Sistema automático de download e processamento
- **Controle de Acesso**: Sistema de autenticação e autorização
- **Tempo Real**: Atualizações em tempo real via WebSocket
- **API REST**: API completa para integração

## 🏗️ Arquitetura

### Backend (Django)
- **Django 4.x**: Framework web principal
- **Django REST Framework**: API REST
- **Channels**: Suporte a WebSocket para tempo real
- **Celery**: Processamento assíncrono (opcional)

### Frontend (React)
- **React 18**: Interface de usuário
- **Vite**: Build tool
- **Tailwind CSS**: Estilização
- **Shadcn/ui**: Componentes UI
- **Socket.io**: Comunicação em tempo real

### Integração WhatsApp
- **WAPI**: Biblioteca personalizada para WhatsApp
- **Webhooks**: Recebimento de mensagens
- **QR Code**: Autenticação via QR Code

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- Git

### Backend
```bash
cd multichat_system
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd multichat-frontend
npm install
npm run dev
```

## 🔧 Configuração

1. Configure as variáveis de ambiente no arquivo `.env`
2. Configure as instâncias do WhatsApp
3. Configure os webhooks para receber mensagens
4. Configure o sistema de mídias

## 📚 Documentação

- [Instruções de Instalação](INSTRUCOES_INSTALACAO.md)
- [Sistema de Webhooks](README_WEBHOOK.md)
- [Sistema de Mídias](README_SISTEMA_MIDIAS.md)
- [Controle de Acesso](SISTEMA_CONTROLE_ACESSO.md)
- [Comandos de Execução](README_COMANDOS.md)

## 🚀 Execução Rápida

### Windows
```bash
# Backend
start_backend.bat

# Frontend
cd multichat-frontend
start_frontend.bat

# Webhook
start_webhook.bat
```

### Linux/Mac
```bash
# Backend
./runBackend.fish

# Frontend
./runFrontend.fish
```

## 📁 Estrutura do Projeto

```
multiChat/
├── multichat_system/          # Backend Django
│   ├── api/                   # API REST
│   ├── authentication/        # Sistema de autenticação
│   ├── core/                  # Modelos principais
│   ├── webhook/               # Sistema de webhooks
│   └── manage.py
├── multichat-frontend/        # Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── contexts/          # Contextos
│   │   └── hooks/             # Hooks customizados
│   └── package.json
├── wapi/                      # Biblioteca WhatsApp
└── web/                       # Utilitários web
```

## 🔒 Segurança

- Autenticação JWT
- Controle de acesso por departamentos
- Validação de entrada
- Sanitização de dados

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato com a equipe de desenvolvimento.

---

**MultiChat System** - Sistema completo de gerenciamento de WhatsApp 
# 🚀 Instruções de Instalação - MultiChat System

## 📦 Conteúdo do Pacote

Este arquivo contém o sistema MultiChat completo com integração W-APi:

- **multichat_system/**: Backend Django com API REST e webhook
- **multichat-frontend/**: Frontend React com interface moderna
- **Documentação**: Relatórios e instruções completas

## 🔧 Pré-requisitos

### Backend (Django)
- Python 3.11+
- MySQL 8.0+
- pip (gerenciador de pacotes Python)

### Frontend (React)
- Node.js 20+
- npm ou pnpm

## 📋 Instalação Passo a Passo

### 1. Extrair o Projeto
```bash
tar -xzf multichat_sistema_completo.tar.gz
cd multichat_sistema_completo/
```

### 2. Configurar Backend Django

#### 2.1 Criar Ambiente Virtual
```bash
cd multichat_system/
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

#### 2.2 Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 2.3 Configurar Banco de Dados
Edite o arquivo `.env`:
```env
DB_NAME=multichat_db
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=sua_chave_secreta_django
DEBUG=True
```

#### 2.4 Executar Migrações
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### 2.5 Iniciar Servidor
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Configurar Frontend React

#### 3.1 Instalar Dependências
```bash
cd ../multichat-frontend/
npm install
# ou
pnpm install
```

#### 3.2 Configurar Variáveis de Ambiente
Crie arquivo `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

#### 3.3 Iniciar Desenvolvimento
```bash
npm run dev
# ou
pnpm dev
```

#### 3.4 Build para Produção
```bash
npm run build
# ou
pnpm build
```

## 🔗 Configuração W-APi

### 1. Webhook URL
Configure na W-APi a URL do webhook:
```
http://seu-dominio.com:8000/webhook/
```

### 2. Credenciais de Teste
Use as credenciais fornecidas:
- **Instância**: 3B6XIW-ZTS923-GEAY6V
- **Token**: Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF

### 3. Conectar Instância
1. Acesse o frontend
2. Vá para "WhatsApp" no menu
3. Clique em "Conectar Instância"
4. Preencha os dados da W-APi
5. Gere QR Code se necessário

## 🌐 Deploy em Produção

### Backend (Django)
1. Configure servidor web (Nginx + Gunicorn)
2. Configure SSL/HTTPS
3. Use banco de dados em produção
4. Configure variáveis de ambiente

### Frontend (React)
1. Execute `npm run build`
2. Sirva arquivos estáticos via Nginx
3. Configure proxy para API

## 📊 Funcionalidades Principais

### ✅ Gestão de Instâncias
- Conectar/desconectar instâncias W-APi
- Monitorar status em tempo real
- Gerar QR Codes para autenticação

### ✅ Processamento de Mensagens
- Receber webhooks automaticamente
- Processar diferentes tipos de mídia
- Organizar conversas por cliente

### ✅ Interface Administrativa
- Dashboard com estatísticas
- Gestão de usuários e clientes
- Monitoramento de eventos

## 🔧 Troubleshooting

### Problemas Comuns

#### Erro de Conexão com Banco
- Verifique credenciais no `.env`
- Confirme se MySQL está rodando
- Execute migrações novamente

#### Frontend não Carrega
- Verifique se backend está rodando
- Confirme URL da API no `.env`
- Limpe cache do navegador

#### Webhook não Funciona
- Verifique se URL está acessível
- Confirme configuração CORS
- Teste endpoint manualmente

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação completa
2. Verifique logs do sistema
3. Teste endpoints individualmente

## 🎯 Próximos Passos

1. **Personalização**: Adapte interface às suas necessidades
2. **Integração**: Conecte com outros sistemas
3. **Monitoramento**: Configure alertas e logs
4. **Backup**: Implemente rotina de backup
5. **Segurança**: Configure firewall e SSL

---

**Versão**: 1.0.0  
**Data**: 11 de julho de 2025  
**Status**: ✅ Pronto para produção


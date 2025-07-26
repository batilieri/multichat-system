# Sistema de Webhook MultiChat

Sistema de webhook para receber e processar dados do WhatsApp Business API, baseado na estrutura do projeto betZap.

## 🚀 Características

- **Baseado no betZap**: Estrutura similar ao projeto betZap para compatibilidade
- **Integração com Django**: Salvamento automático no banco de dados
- **Processamento em tempo real**: Detecção e processamento automático de mensagens
- **Múltiplos clientes**: Suporte a múltiplos clientes com identificação por ID
- **Interface admin**: Gerenciamento via Django Admin
- **Túnel público**: Integração com ngrok para receber webhooks externos
- **Estatísticas**: Sistema completo de estatísticas e métricas

## 📋 Estrutura do Sistema

### Modelos de Dados

- **WebhookEvent**: Armazena todos os eventos recebidos
- **Chat**: Representa conversas/contatos
- **Sender**: Representa remetentes/destinatários
- **Message**: Mensagens individuais
- **MessageStats**: Estatísticas de mensagens por período
- **ContactStats**: Estatísticas de contatos
- **RealTimeStats**: Estatísticas em tempo real

### Processadores

- **WhatsAppWebhookProcessor**: Processa dados do WhatsApp
- **WebhookValidator**: Valida e sanitiza dados

### Views

- **WebhookView**: Endpoint principal para receber webhooks
- **WebhookStatusView**: Status e estatísticas
- **WebhookTestView**: Testes do sistema
- **WebhookEventsView**: Listagem de eventos

## 🛠️ Instalação

### 1. Instalar Dependências

```bash
# Instalar dependências do webhook
pip install -r requirements_webhook.txt
```

### 2. Executar Migrações

```bash
# Criar migrações
python manage.py makemigrations webhook

# Aplicar migrações
python manage.py migrate webhook
```

### 3. Configurar Sistema

```bash
# Executar script de configuração
python setup_webhook.py
```

## 🚀 Uso

### Servidor Webhook Local

```bash
# Iniciar servidor webhook local (com ngrok)
python webhook/servidor_webhook_local.py
```

O servidor irá:
- Configurar automaticamente o token do ngrok
- Criar túnel público HTTPS
- Detectar automaticamente dados do WhatsApp
- Salvar dados no banco Django

### Servidor Django

```bash
# Iniciar servidor Django
python manage.py runserver
```

### Testar Sistema

```bash
# Executar testes completos
python test_webhook.py
```

## 📡 Endpoints

### Webhook Local (Flask)
- **Principal**: `http://localhost:5000/webhook`
- **Status**: `http://localhost:5000/status`
- **Teste**: `http://localhost:5000/test`

### Webhook Django
- **Principal**: `http://localhost:8000/webhook/`
- **Status**: `http://localhost:8000/webhook/status/`
- **Teste**: `http://localhost:8000/webhook/test/`
- **Eventos**: `http://localhost:8000/webhook/events/`

## 📊 Dados Processados

### Estrutura do WhatsApp

O sistema processa dados no formato do WhatsApp Business API:

```json
{
  "instanceId": "instance_123",
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": false,
    "id": "message_id_123"
  },
  "message": {
    "conversationMessage": {
      "conversation": "Texto da mensagem"
    }
  },
  "messageTimestamp": "1640995200",
  "pushName": "Nome do Usuário",
  "msgContent": {
    "conversation": "Texto da mensagem"
  }
}
```

### Tipos de Mensagem Suportados

- **text**: Mensagens de texto
- **image**: Imagens
- **video**: Vídeos
- **audio**: Áudios
- **document**: Documentos
- **sticker**: Stickers
- **location**: Localização
- **contact**: Contatos

## 🔧 Configuração

### Identificação de Cliente

O sistema identifica o cliente através de:

1. **instanceId**: Campo específico do WhatsApp
2. **cliente_id**: Campo personalizado
3. **Fallback**: Primeiro cliente ativo (desenvolvimento)

### Configuração do Ngrok

O token do ngrok está configurado no arquivo `servidor_webhook_local.py`:

```python
NGROK_TOKEN = "249wILexYz7XZWEYPPd4ECjyzzr_2Q8e91e1G9EYEsEtNxNsa"
```

## 📈 Estatísticas

### Métricas Coletadas

- **Mensagens**: Total, recebidas, enviadas
- **Tipos**: Texto, mídia, documentos
- **Status**: Entregues, lidas
- **Tempo real**: Chats ativos, mensagens pendentes
- **Performance**: Tempo de resposta, taxa de mensagens

### Visualização

Acesse o Django Admin para visualizar:
- Eventos de webhook
- Chats e mensagens
- Estatísticas detalhadas
- Remetentes e contatos

## 🧪 Testes

### Teste Manual

```bash
# Enviar dados de teste
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "instanceId": "test_instance",
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "test_message_123"
    },
    "message": {
      "conversationMessage": {
        "conversation": "Mensagem de teste"
      }
    },
    "messageTimestamp": "1640995200",
    "pushName": "Usuário Teste",
    "msgContent": {
      "conversation": "Mensagem de teste"
    }
  }'
```

### Teste Automatizado

```bash
# Executar suite de testes
python test_webhook.py
```

## 🔍 Monitoramento

### Logs

O sistema gera logs detalhados:
- Requisições recebidas
- Dados processados
- Erros e exceções
- Estatísticas de processamento

### Status em Tempo Real

Acesse `/status` para ver:
- Total de requisições
- URL do túnel ngrok
- Status do processamento
- Estatísticas por cliente

## 🚨 Solução de Problemas

### Erro de Conexão

```bash
# Verificar se o servidor está rodando
curl http://localhost:5000/status
```

### Erro de Migração

```bash
# Recriar migrações
python manage.py makemigrations webhook --empty
python manage.py makemigrations webhook
python manage.py migrate webhook
```

### Erro de Dependências

```bash
# Reinstalar dependências
pip install -r requirements_webhook.txt --force-reinstall
```

## 📚 Integração com WhatsApp Business API

### Configuração no WhatsApp

1. Acesse o painel do WhatsApp Business API
2. Configure o webhook com a URL do ngrok
3. Exemplo: `https://abc123.ngrok.io/webhook`
4. Ative os eventos desejados

### Eventos Suportados

- **message**: Mensagens recebidas
- **status**: Status de entrega
- **qrCode**: Código QR para conexão
- **connection**: Status de conexão

## 🔐 Segurança

### Validação de Dados

- Sanitização automática de dados sensíveis
- Validação de estrutura JSON
- Verificação de campos obrigatórios
- Proteção contra dados maliciosos

### Autenticação

- CSRF desabilitado para webhooks
- Validação por IP (configurável)
- Logs de todas as requisições

## 📝 Desenvolvimento

### Estrutura de Arquivos

```
webhook/
├── models.py          # Modelos de dados
├── processors.py      # Processadores
├── views.py          # Views do Django
├── urls.py           # URLs
├── admin.py          # Interface admin
├── servidor_webhook_local.py  # Servidor Flask
└── migrations/       # Migrações
```

### Adicionando Novos Tipos

1. Atualizar `_extract_message_type()` em `processors.py`
2. Adicionar campos no modelo `Message`
3. Atualizar estatísticas em `_update_stats()`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação do Django
- Verifique os logs do sistema

---

**Desenvolvido baseado na estrutura do betZap para máxima compatibilidade com sistemas existentes.** 
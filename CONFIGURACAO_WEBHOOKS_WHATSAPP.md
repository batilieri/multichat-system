# 🔗 Configuração de Webhooks WhatsApp - MultiChat System

## 📋 Visão Geral

Este documento detalha a configuração completa dos webhooks do WhatsApp para o sistema MultiChat, conforme especificação do usuário.

## 🌐 Endpoints de Webhook Disponíveis

### **1. 🔗 Ao Conectar o WhatsApp na Instância**
```http
POST https://meulink.com/webhook/connect/
```

**Propósito**: Processar eventos de conexão da instância do WhatsApp
**Eventos capturados**:
- ✅ Instância conectada com sucesso
- ✅ QR Code escaneado
- ✅ Status online
- ✅ Autenticação bem-sucedida

**Exemplo de payload**:
```json
{
  "instanceId": "instance_123",
  "event": "connection",
  "status": "connected",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### **2. ❌ Ao Desconectar da Instância**
```http
POST https://meulink.com/webhook/disconnect/
```

**Propósito**: Processar eventos de desconexão da instância
**Eventos capturados**:
- ✅ Instância desconectada
- ✅ Status offline
- ✅ Log de desconexão
- ✅ Limpeza de sessão

**Exemplo de payload**:
```json
{
  "instanceId": "instance_123",
  "event": "disconnection",
  "status": "disconnected",
  "timestamp": "2025-01-15T10:35:00Z"
}
```

### **3. 📤 Ao Enviar uma Mensagem**
```http
POST https://ac70b57623e8.ngrok-free.app/webhook/send-message/
```

**Propósito**: Processar mensagens enviadas pelo usuário
**Características**:
- ✅ `fromMe: true`
- ✅ Remetente = nome do cliente
- ✅ Aparece do lado direito no frontend
- ✅ Status de entrega visível

**Exemplo de payload**:
```json
{
  "instanceId": "instance_123",
  "event": "message",
  "fromMe": true,
  "messageId": "msg_456",
  "sender": {
    "id": "5511999999999@c.us",
    "name": "Cliente Nome"
  },
  "chat": {
    "id": "5511888888888@c.us",
    "name": "Contato Destino"
  },
  "msgContent": {
    "type": "text",
    "text": "Olá, como posso ajudar?"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### **4. 📥 Ao Receber uma Mensagem**
```http
POST https://ac70b57623e8.ngrok-free.app/webhook/receive-message/
```

**Propósito**: Processar mensagens recebidas de outros
**Características**:
- ✅ `fromMe: false`
- ✅ Remetente = nome do contato
- ✅ Aparece do lado esquerdo no frontend
- ✅ Sem status de entrega

**Exemplo de payload**:
```json
{
  "instanceId": "instance_123",
  "event": "message",
  "fromMe": false,
  "messageId": "msg_789",
  "sender": {
    "id": "5511888888888@c.us",
    "name": "Contato Nome"
  },
  "chat": {
    "id": "5511888888888@c.us",
    "name": "Contato Nome"
  },
  "msgContent": {
    "type": "text",
    "text": "Preciso de ajuda!"
  },
  "timestamp": "2025-01-15T10:31:00Z"
}
```

### **5. 👥 Presença do Chat**
```http
POST https://meulink.com/webhook/chat-presence/
```

**Propósito**: Processar eventos de presença do chat
**Eventos capturados**:
- ✅ Digitação em andamento
- ✅ Presença online/offline
- ✅ Atualização de status
- ✅ Indicadores de atividade

**Exemplo de payload**:
```json
{
  "instanceId": "instance_123",
  "event": "presence",
  "chatId": "5511888888888@c.us",
  "presence": "composing",
  "timestamp": "2025-01-15T10:32:00Z"
}
```

### **6. 📊 Receber Status da Mensagem**
```http
POST https://ac70b57623e8.ngrok-free.app/webhook/message-status/
```

**Propósito**: Processar mudanças de status da mensagem
**Status suportados**:
- ✅ Enviado → Entregue → Lido
- ✅ Atualização em tempo real
- ✅ Histórico de status
- ✅ Confirmações de entrega

**Exemplo de payload**:
```json
{
  "instanceId": "instance_123",
  "event": "message_status",
  "messageId": "msg_456",
  "status": "delivered",
  "timestamp": "2025-01-15T10:33:00Z"
}
```

### **7. 📋 Webhook Principal (Fallback)**
```http
POST https://ac70b57623e8.ngrok-free.app/webhook/
```

**Propósito**: Processar todos os tipos de evento (compatibilidade)
**Características**:
- ✅ Identificação automática do tipo
- ✅ Roteamento interno
- ✅ Compatibilidade com sistemas antigos

## ⚙️ Configuração no WhatsApp Business API

### **Configuração na W-API**

1. **Acesse o painel da W-API**
2. **Configure os webhooks para cada instância**:

```javascript
// Configuração de webhooks por instância
const webhookConfig = {
  "instance_123": {
    "connection": "https://meulink.com/webhook/connect/",
    "disconnection": "https://meulink.com/webhook/disconnect/",
    "send_message": "https://ac70b57623e8.ngrok-free.app/webhook/send-message/",
    "receive_message": "https://ac70b57623e8.ngrok-free.app/webhook/receive-message/",
    "chat_presence": "https://meulink.com/webhook/chat-presence/",
    "message_status": "https://ac70b57623e8.ngrok-free.app/webhook/message-status/",
    "fallback": "https://ac70b57623e8.ngrok-free.app/webhook/"
  }
}
```

### **Configuração via API**

```bash
# Configurar webhooks para uma instância
curl -X POST "https://api.w-api.app/webhook/set" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "instanceId": "instance_123",
    "webhooks": {
      "connection": "https://meulink.com/webhook/connect/",
      "disconnection": "https://meulink.com/webhook/disconnect/",
      "send_message": "https://ac70b57623e8.ngrok-free.app/webhook/send-message/",
      "receive_message": "https://ac70b57623e8.ngrok-free.app/webhook/receive-message/",
      "chat_presence": "https://meulink.com/webhook/chat-presence/",
      "message_status": "https://ac70b57623e8.ngrok-free.app/webhook/message-status/"
    }
  }'
```

## 🔧 Implementação no Sistema

### **Estrutura de Arquivos**

```
📁 multichat_system/webhook/
├── 📄 views.py              # Views dos webhooks
├── 📄 urls.py               # URLs dos endpoints
├── 📄 models.py             # Modelos de dados
├── 📄 signals.py            # Sinais para processamento
└── 📄 media_processor.py    # Processamento de mídias
```

### **Endpoints Implementados**

✅ **Todos os endpoints já estão implementados** no sistema:

1. `webhook_connect()` - Processa conexões
2. `webhook_disconnect()` - Processa desconexões
3. `webhook_send_message()` - Processa mensagens enviadas
4. `webhook_receive_message()` - Processa mensagens recebidas
5. `webhook_chat_presence()` - Processa presença
6. `webhook_message_status()` - Processa status
7. `webhook_receiver()` - Webhook principal (fallback)

### **Funcionalidades Implementadas**

- ✅ **Identificação automática** de `from_me`
- ✅ **Processamento específico** por tipo de evento
- ✅ **Salvamento no banco** Django
- ✅ **Processamento de mídias** automático
- ✅ **Logs organizados** por categoria
- ✅ **Tratamento de erros** robusto

## 🧪 Testes e Validação

### **Teste de Conectividade**

```bash
# Testar webhook de conexão
curl -X POST "https://meulink.com/webhook/connect/" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceId": "test_instance",
    "event": "connection",
    "status": "connected"
  }'
```

### **Teste de Mensagem**

```bash
# Testar webhook de mensagem enviada
curl -X POST "https://ac70b57623e8.ngrok-free.app/webhook/send-message/" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceId": "test_instance",
    "event": "message",
    "fromMe": true,
    "messageId": "test_msg_123",
    "sender": {"id": "5511999999999@c.us", "name": "Teste"},
    "msgContent": {"type": "text", "text": "Teste de mensagem"}
  }'
```

## 📊 Monitoramento

### **Logs do Sistema**

```python
# Exemplo de logs gerados
logger.info("🔗 Webhook de conexão processado: instance_123")
logger.info("📤 Mensagem enviada processada: msg_456")
logger.info("📥 Mensagem recebida processada: msg_789")
logger.info("👥 Presença do chat atualizada")
logger.info("📊 Status da mensagem atualizado: delivered")
```

### **Métricas Disponíveis**

- 📈 **Taxa de entrega** de webhooks
- ⏱️ **Tempo de resposta** dos endpoints
- 🔍 **Eventos processados** por tipo
- ❌ **Erros e falhas** de processamento

## 🚀 Próximos Passos

1. **Configurar URLs** no painel da W-API
2. **Testar conectividade** dos webhooks
3. **Validar processamento** dos eventos
4. **Monitorar logs** do sistema
5. **Ajustar configurações** conforme necessário

## 📞 Suporte

Para dúvidas ou problemas com a configuração dos webhooks:

- 📧 **Email**: suporte@multichat.com
- 📱 **WhatsApp**: +55 11 99999-9999
- 📋 **Documentação**: [docs.multichat.com](https://docs.multichat.com)

---

**Versão**: 1.0  
**Data**: 15/01/2025  
**Autor**: Sistema MultiChat 
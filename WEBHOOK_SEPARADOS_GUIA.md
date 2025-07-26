# 🚀 Guia Completo: Webhooks Separados - MultiChat System

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura dos Webhooks Separados](#arquitetura)
3. [Endpoints Disponíveis](#endpoints)
4. [Implementação Passo a Passo](#implementação)
5. [Configuração no WhatsApp Business API](#configuração)
6. [Testes e Validação](#testes)
7. [Troubleshooting](#troubleshooting)
8. [Exemplos de Uso](#exemplos)

---

## 🎯 Visão Geral

### **Problema Resolvido**
- ❌ **Antes**: Todas as mensagens marcadas como `fromMe: false`
- ❌ **Antes**: Dificuldade em identificar mensagens enviadas vs recebidas
- ❌ **Antes**: Processamento genérico para todos os tipos de evento
- ✅ **Agora**: Identificação automática de mensagens enviadas/recebidas
- ✅ **Agora**: Processamento específico por tipo de evento
- ✅ **Agora**: Separação clara entre diferentes tipos de webhook

### **Benefícios da Separação**
- 🎯 **Processamento específico** por tipo de evento
- 🔍 **Identificação automática** de `from_me`
- 📊 **Logs organizados** por categoria
- 🚀 **Performance melhorada** com processamento direcionado
- 🔧 **Manutenção facilitada** com endpoints específicos

---

## 🏗️ Arquitetura dos Webhooks Separados

### **Estrutura de Endpoints**
```
📁 /webhook/
├── 📤 /send-message/     # Mensagens enviadas pelo usuário
├── 📥 /receive-message/  # Mensagens recebidas de outros
├── 👥 /chat-presence/    # Presença do chat
├── 📊 /message-status/   # Status da mensagem
├── 🔗 /connect/          # Conexão da instância
├── ❌ /disconnect/       # Desconexão da instância
└── 📋 /                  # Webhook principal (fallback)
```

### **Fluxo de Processamento**
```
1. 📥 Webhook recebido
2. 🔍 Identificação do tipo de evento
3. 🎯 Roteamento para endpoint específico
4. ⚙️ Processamento especializado
5. 💾 Salvamento no banco Django
6. 📤 Resposta com status
```

---

## 🌐 Endpoints Disponíveis

### **1. 📤 Webhook Send Message**
```http
POST /webhook/send-message/
```
**Propósito**: Processar mensagens enviadas pelo usuário
**Características**:
- ✅ `fromMe: true`
- ✅ Remetente = nome do cliente
- ✅ Aparece do lado direito no frontend
- ✅ Status de entrega visível

### **2. 📥 Webhook Receive Message**
```http
POST /webhook/receive-message/
```
**Propósito**: Processar mensagens recebidas de outros
**Características**:
- ✅ `fromMe: false`
- ✅ Remetente = nome do contato
- ✅ Aparece do lado esquerdo no frontend
- ✅ Sem status de entrega

### **3. 👥 Webhook Chat Presence**
```http
POST /webhook/chat-presence/
```
**Propósito**: Processar eventos de presença do chat
**Características**:
- ✅ Digitação em andamento
- ✅ Presença online/offline
- ✅ Atualização de status

### **4. 📊 Webhook Message Status**
```http
POST /webhook/message-status/
```
**Propósito**: Processar mudanças de status da mensagem
**Características**:
- ✅ Enviado → Entregue → Lido
- ✅ Atualização em tempo real
- ✅ Histórico de status

### **5. 🔗 Webhook Connect**
```http
POST /webhook/connect/
```
**Propósito**: Processar conexão da instância
**Características**:
- ✅ Instância conectada
- ✅ QR Code escaneado
- ✅ Status online

### **6. ❌ Webhook Disconnect**
```http
POST /webhook/disconnect/
```
**Propósito**: Processar desconexão da instância
**Características**:
- ✅ Instância desconectada
- ✅ Status offline
- ✅ Log de desconexão

### **7. 📋 Webhook Principal (Fallback)**
```http
POST /webhook/
```
**Propósito**: Processar todos os tipos de evento (compatibilidade)
**Características**:
- ✅ Identificação automática do tipo
- ✅ Roteamento interno
- ✅ Compatibilidade com sistemas antigos

---

## 🔧 Implementação Passo a Passo

### **Passo 1: Criar URLs Separadas**
```python
# webhook/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Webhook principal (fallback)
    path('', views.webhook_receiver, name='webhook_receiver'),
    
    # Webhooks específicos
    path('send-message/', views.webhook_send_message, name='webhook_send_message'),
    path('receive-message/', views.webhook_receive_message, name='webhook_receive_message'),
    path('chat-presence/', views.webhook_chat_presence, name='webhook_chat_presence'),
    path('message-status/', views.webhook_message_status, name='webhook_message_status'),
    path('connect/', views.webhook_connect, name='webhook_connect'),
    path('disconnect/', views.webhook_disconnect, name='webhook_disconnect'),
]
```

### **Passo 2: Implementar Funções de Processamento**
```python
# webhook/views.py

@csrf_exempt
def webhook_send_message(request):
    """Webhook específico para mensagens enviadas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"📤 WEBHOOK ENVIAR MENSAGEM: {webhook_data}")
        
        # Processar apenas mensagens enviadas (fromMe: true)
        if webhook_data.get('fromMe') or webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'send_message')
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Não é mensagem enviada'})
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook send_message: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)
```

### **Passo 3: Função de Identificação from_me**
```python
# api/utils.py

def determine_from_me_saas(payload, instance_id):
    """
    Determina se a mensagem foi enviada pelo próprio usuário (from_me).
    - Método 1: Campo fromMe do WhatsApp (mais confiável)
    - Método 2: Comparar sender com instance_id
    """
    message_key = payload.get('key', {})
    if 'fromMe' in message_key:
        return message_key['fromMe']
    
    sender_id = payload.get('sender', {}).get('id', '')
    sender_phone = sender_id.split('@')[0] if '@' in sender_id else sender_id
    
    # Se o instance_id contém o número do sender, é do proprietário
    if sender_phone and sender_phone in instance_id:
        return True
    
    return False
```

### **Passo 4: Função de Salvamento com from_me**
```python
def save_message_to_chat_with_from_me(payload, event, from_me, cliente):
    """
    Salva a mensagem no sistema de chats principal com from_me já determinado
    """
    try:
        chat_id = payload.get("chat", {}).get("id", "")
        message_key = payload.get('key', {})
        message_id = message_key.get('id', '')
        
        # DETERMINAR REMETENTE BASEADO EM from_me E CLIENTE
        if from_me:
            remetente = cliente.nome if cliente else "Usuário"
        else:
            sender_data = payload.get('sender', {})
            remetente = sender_data.get('pushName', '') or sender_data.get('name', '') or chat_id.split('@')[0]
        
        # Criar mensagem com from_me já determinado
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente=remetente,
            conteudo=content,
            tipo=message_type,
            lida=False,
            from_me=from_me,  # Usar o valor já determinado
            message_id=message_id
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar mensagem: {e}")
        return False
```

---

## ⚙️ Configuração no WhatsApp Business API

### **1. URLs para Configurar**
```
🌐 URL Principal: https://[ngrok-url]/webhook/
📤 Mensagens Enviadas: https://[ngrok-url]/webhook/send-message/
📥 Mensagens Recebidas: https://[ngrok-url]/webhook/receive-message/
👥 Presença do Chat: https://[ngrok-url]/webhook/chat-presence/
📊 Status da Mensagem: https://[ngrok-url]/webhook/message-status/
🔗 Conexão: https://[ngrok-url]/webhook/connect/
❌ Desconexão: https://[ngrok-url]/webhook/disconnect/
```

### **2. Configuração no Painel**
1. **Acesse** o painel da WhatsApp Business API
2. **Vá para** Configurações > Webhooks
3. **Configure** cada endpoint separadamente
4. **Teste** cada URL individualmente
5. **Ative** o webhook principal como fallback

### **3. Exemplo de Configuração**
```json
{
  "webhooks": {
    "send_message": "https://abc123.ngrok-free.app/webhook/send-message/",
    "receive_message": "https://abc123.ngrok-free.app/webhook/receive-message/",
    "chat_presence": "https://abc123.ngrok-free.app/webhook/chat-presence/",
    "message_status": "https://abc123.ngrok-free.app/webhook/message-status/",
    "connect": "https://abc123.ngrok-free.app/webhook/connect/",
    "disconnect": "https://abc123.ngrok-free.app/webhook/disconnect/",
    "fallback": "https://abc123.ngrok-free.app/webhook/"
  }
}
```

---

## 🧪 Testes e Validação

### **1. Teste Individual dos Endpoints**
```bash
# Teste mensagem enviada
curl -X POST https://abc123.ngrok-free.app/webhook/send-message/ \
  -H "Content-Type: application/json" \
  -d '{"fromMe": true, "message": "teste"}'

# Teste mensagem recebida
curl -X POST https://abc123.ngrok-free.app/webhook/receive-message/ \
  -H "Content-Type: application/json" \
  -d '{"fromMe": false, "message": "teste"}'
```

### **2. Verificação no Banco de Dados**
```python
# Verificar mensagens salvas
from core.models import Mensagem

# Mensagens enviadas
mensagens_enviadas = Mensagem.objects.filter(from_me=True)
print(f"Mensagens enviadas: {mensagens_enviadas.count()}")

# Mensagens recebidas
mensagens_recebidas = Mensagem.objects.filter(from_me=False)
print(f"Mensagens recebidas: {mensagens_recebidas.count()}")
```

### **3. Logs de Debug**
```bash
# Verificar logs do webhook
tail -f logs/webhook.log

# Verificar logs do Django
python manage.py runserver --verbosity=2
```

---

## 🔧 Troubleshooting

### **Problema 1: Mensagens não aparecem**
**Sintoma**: Webhook recebido mas mensagem não salva
**Solução**:
```python
# Verificar se o cliente existe
cliente = Cliente.objects.filter(ativo=True).first()
if not cliente:
    print("❌ Nenhum cliente ativo encontrado")

# Verificar se a instância existe
instance = WhatsappInstance.objects.filter(instance_id=instance_id).first()
if not instance:
    print(f"❌ Instância {instance_id} não encontrada")
```

### **Problema 2: from_me sempre false**
**Sintoma**: Todas as mensagens marcadas como recebidas
**Solução**:
```python
# Verificar dados do webhook
print(f"📤 Dados do webhook: {webhook_data}")
print(f"🔍 fromMe: {webhook_data.get('fromMe')}")
print(f"🔑 message_key: {webhook_data.get('key', {})}")

# Verificar função determine_from_me_saas
from_me = determine_from_me_saas(webhook_data, instance_id)
print(f"✅ from_me determinado: {from_me}")
```

### **Problema 3: Endpoint não responde**
**Sintoma**: 404 ou timeout no webhook
**Solução**:
```bash
# Verificar se o servidor está rodando
python manage.py runserver 8000

# Verificar URLs
python manage.py show_urls | grep webhook

# Testar endpoint localmente
curl -X POST http://localhost:8000/webhook/send-message/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## 📝 Exemplos de Uso

### **Exemplo 1: Mensagem de Texto Enviada**
```json
{
  "event": "webhookReceived",
  "instanceId": "ABC123",
  "messageId": "msg_123",
  "sender": {
    "id": "5511999999999@s.whatsapp.net",
    "pushName": "João Silva"
  },
  "chat": {
    "id": "5511888888888@s.whatsapp.net"
  },
  "msgContent": {
    "conversation": "Olá, como vai?"
  },
  "fromMe": true,
  "moment": 1752894203
}
```

**Resultado**:
- ✅ `from_me: true`
- ✅ `remetente: "João Silva"` (nome do cliente)
- ✅ Aparece do lado direito no frontend
- ✅ Status de entrega visível

### **Exemplo 2: Mensagem de Texto Recebida**
```json
{
  "event": "webhookReceived",
  "instanceId": "ABC123",
  "messageId": "msg_124",
  "sender": {
    "id": "5511888888888@s.whatsapp.net",
    "pushName": "Maria Santos"
  },
  "chat": {
    "id": "5511888888888@s.whatsapp.net"
  },
  "msgContent": {
    "conversation": "Oi! Tudo bem!"
  },
  "fromMe": false,
  "moment": 1752894300
}
```

**Resultado**:
- ✅ `from_me: false`
- ✅ `remetente: "Maria Santos"`
- ✅ Aparece do lado esquerdo no frontend
- ✅ Sem status de entrega

### **Exemplo 3: Status de Mensagem**
```json
{
  "event": "messageStatus",
  "instanceId": "ABC123",
  "messageId": "msg_123",
  "status": "read",
  "timestamp": 1752894400
}
```

**Resultado**:
- ✅ Status atualizado para "lido"
- ✅ Timestamp de leitura registrado
- ✅ Frontend atualizado em tempo real

---

## 🎉 Conclusão

### **✅ Benefícios Alcançados**
1. **Identificação automática** de mensagens enviadas vs recebidas
2. **Processamento específico** por tipo de evento
3. **Logs organizados** e fáceis de debugar
4. **Performance melhorada** com roteamento direcionado
5. **Manutenção facilitada** com endpoints separados

### **🚀 Próximos Passos**
1. **Configurar** URLs no WhatsApp Business API
2. **Testar** todos os tipos de mensagem
3. **Monitorar** logs para otimizações
4. **Implementar** métricas de performance
5. **Documentar** casos de uso específicos

---

**📚 Documentação criada para o projeto MultiChat System - Webhooks Separados**  
**🔄 Última atualização**: 19/07/2025  
**👨‍💻 Desenvolvido por**: Assistente AI + Elizeu Batiliere 
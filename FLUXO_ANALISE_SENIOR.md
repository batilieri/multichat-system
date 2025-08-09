# 🔍 FLUXO DETALHADO PARA ANÁLISE SÊNIOR

## 📋 SITUAÇÃO ATUAL

**PROBLEMA**: Download automático funciona em testes manuais, mas falha no webhook real em tempo real.

**EVIDÊNCIA**: 
- ✅ Teste manual: `debug_simples.py` baixa arquivo com sucesso
- ❌ Webhook real: Usuário envia áudio → nenhum arquivo aparece na pasta
- ⚠️ Logs silenciosos: Django não mostra prints da função no console

---

## 🏗️ ARQUITETURA DO SISTEMA

### 📡 Fluxo do Webhook
```
1. WhatsApp → W-API → Webhook URL → Django
2. Django: /webhook/send-message → webhook_send_message()
3. Django: webhook_send_message() → process_webhook_message()
4. Django: process_webhook_message() → process_media_automatically()
5. Django: process_media_automatically() → download_media_via_wapi()
6. Django: download_media_via_wapi() → reorganizar_arquivo_por_cliente()
```

### 📂 Estrutura de Arquivos Esperada
```
multichat_system/media_storage/
├── NOME_CLIENTE/
│   └── instance_INSTANCE_ID/
│       └── chats/
│           └── CHAT_ID/
│               └── audio/
│                   └── wapi_download_*.mp3
```

---

## 🧪 TESTES REALIZADOS

### ✅ TESTE 1: Função Individual (SUCESSO)
```bash
python debug_simples.py
```
**Resultado**: 
- ✅ Arquivo baixado: `9397 bytes`
- ✅ Estrutura criada corretamente
- ✅ W-API responde: Status 200
- ✅ Logs detalhados aparecem

### ❌ TESTE 2: Webhook Real (FALHA)
```bash
python monitorar_webhook_tempo_real.py
```
**Resultado**:
- ✅ 40 webhooks recebidos com áudio
- ✅ Todos marcados como `processed: True`
- ❌ 0 arquivos baixados
- ❌ Nenhum log da função aparece

---

## 🔍 PONTOS DE FALHA IDENTIFICADOS

### 1. 🚨 ENDPOINT CORRECTION NEEDED
**Suspeita**: Webhook real usa endpoint diferente do teste

**Verificar**:
```python
# Arquivo: multichat_system/webhook/urls.py
# Linha 29: path('send-message/', webhook_send_message, name='webhook_send_message')
# 
# Confirmar se webhook real está chamando /webhook/send-message/
```

### 2. 🚨 CONDIÇÃO DE BYPASS
**Suspeita**: `webhook_send_message()` tem condição que impede processamento

**Verificar**:
```python
# Arquivo: multichat_system/webhook/views.py
# Linhas 214-217:
if webhook_data.get('fromMe') or webhook_data.get('data', {}).get('fromMe'):
    return process_webhook_message(webhook_data, 'send_message')
else:
    return JsonResponse({'status': 'ignored', 'message': 'Não é mensagem enviada'})
```

**Problema potencial**: Se `fromMe` for `False`, webhook é ignorado!

### 3. 🚨 LOGS SILENCIOSOS
**Suspeita**: Django em produção não mostra prints

**Verificar**:
- Configuração de logging no `settings.py`
- Se `DEBUG = False`
- Se prints chegam ao console vs logs

### 4. 🚨 RACE CONDITION
**Suspeita**: Webhook duplicado causando conflito

**Evidência**: Monitor mostrou webhooks duplicados para mesmo messageId
```
🆔 Message ID: C8B033F71EEA4B8402BB9774CCA435CD (apareceu 2x)
```

---

## 🔧 PLANO DE INVESTIGAÇÃO SÊNIOR

### ETAPA 1: Confirmar Endpoint Correto
```bash
# 1. Verificar logs do servidor Django em tempo real
# 2. Enviar áudio
# 3. Confirmar qual endpoint foi chamado
# 4. Verificar se chegou até process_media_automatically()
```

### ETAPA 2: Debug do Fluxo Webhook
```python
# Adicionar logs em cada função:
# 1. webhook_send_message() - log de entrada
# 2. process_webhook_message() - log de dados
# 3. process_media_automatically() - log detalhado
# 4. download_media_via_wapi() - log da W-API
```

### ETAPA 3: Verificar Condições de Bypass
```python
# Investigar se webhook está sendo ignorado por:
# 1. fromMe == False
# 2. Dados insuficientes
# 3. Validação de instância falhando
# 4. Token inválido/expirado
```

### ETAPA 4: Comparar Estrutura de Dados
```python
# Comparar dados do webhook real vs teste:
# 1. Estrutura do messageContent
# 2. Formato dos campos mediaKey/directPath
# 3. Dados de autenticação (instanceId/token)
```

---

## 🛠️ SCRIPTS DE DEBUG FORNECIDOS

### 1. Monitor Tempo Real
```bash
python monitorar_webhook_tempo_real.py
# Monitora webhooks e arquivos em tempo real
```

### 2. Debug Individual
```bash
python debug_simples.py
# Testa função process_media_automatically isoladamente
```

### 3. Investigação Completa
```bash
python investigar_webhook_real.py
# Analisa estrutura de webhooks e compara com testes
```

---

## 🎯 HIPÓTESES PRIORITÁRIAS

### HIPÓTESE 1: Webhook Ignorado (MAIS PROVÁVEL)
**Causa**: `fromMe: False` em mensagens recebidas
**Solução**: Modificar condição em `webhook_send_message()`
**Verificação**: Log do campo `fromMe` em webhook real

### HIPÓTESE 2: Logs Silenciosos (PROVÁVEL)
**Causa**: Django não mostra prints em produção
**Solução**: Usar `logging` em vez de `print`
**Verificação**: Adicionar logger.info() nas funções

### HIPÓTESE 3: Race Condition (POSSÍVEL)
**Causa**: Webhooks duplicados causando conflito
**Solução**: Verificar se message_id já foi processado
**Verificação**: Log de messageId duplicados

### HIPÓTESE 4: Token Expirado (POSSÍVEL)
**Causa**: Token W-API expirou desde último teste
**Solução**: Verificar status do token
**Verificação**: Testar W-API manualmente

---

## 📊 DADOS PARA ANÁLISE

### Webhook Real Recente (Exemplo)
```json
{
  "event": "webhookDelivery",
  "instanceId": "3B6XIW-ZTS923-GEAY6V",
  "messageId": "C8B033F71EEA4B8402BB9774CCA435CD",
  "fromMe": true,
  "msgContent": {
    "audioMessage": {
      "mediaKey": "JHnL95dYbmJt...",
      "directPath": "/v/t62.7117-24/...",
      "mimetype": "audio/ogg; codecs=opus"
    }
  }
}
```

### Teste Manual (Funcionou)
```json
{
  "event": "webhookDelivery", 
  "instanceId": "3B6XIW-ZTS923-GEAY6V",
  "messageId": "E93A86D6119804FE8714DF3CAED360B6",
  "fromMe": true,
  "msgContent": {
    "audioMessage": {
      "mediaKey": "cMVqM8QbTKnL...",
      "directPath": "/v/t62.7117-24/...",
      "mimetype": "audio/ogg; codecs=opus"
    }
  }
}
```

---

## 🚀 AÇÕES IMEDIATAS RECOMENDADAS

### 1. **LOGGING URGENTE**
```python
# Adicionar em webhook/views.py:
import logging
logger = logging.getLogger(__name__)

# Substituir todos os print() por logger.info()
```

### 2. **DEBUG CONDIÇÃO FROMMEE**
```python
# Em webhook_send_message(), adicionar:
logger.info(f"🔍 fromMe check: {webhook_data.get('fromMe')} | data.fromMe: {webhook_data.get('data', {}).get('fromMe')}")
```

### 3. **VERIFICAR ENDPOINT REAL**
```bash
# Monitorar logs Django durante envio de áudio
tail -f django.log  # ou equivalente
```

### 4. **TESTE DIRETO W-API**
```bash
# Verificar se token ainda funciona
python verificar_tokens_banco.py
```

---

## 📞 SUPORTE ADICIONAL

### Arquivos Modificados Recentemente
- `multichat_system/webhook/views.py` (função process_media_automatically)
- `multichat_system/webhook/urls.py` (rotas webhook)

### Comandos de Debug
```bash
# Verificar estrutura atual
Get-ChildItem "multichat_system\media_storage\Elizeu_Batiliere_Dos_Santos\" -Recurse

# Monitorar logs Django
python manage.py runserver --verbosity=2

# Teste isolado
python debug_simples.py
```

---

## ⚠️ PRIORIDADE MÁXIMA

**A diferença entre teste manual (funciona) e webhook real (falha) indica problema no FLUXO DE CHAMADA, não na função em si.**

**Foco**: Verificar por que `process_media_automatically()` não está sendo executada no webhook real, mesmo com webhooks sendo marcados como `processed: True`. 
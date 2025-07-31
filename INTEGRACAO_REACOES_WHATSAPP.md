# Integração de Reações com WhatsApp Real

## 🎯 Objetivo

Quando uma reação for adicionada a uma mensagem no sistema, ela também deve aparecer no WhatsApp real do contato.

## 🔧 Implementação

### 1. **Backend Django (views.py)**

O endpoint `/api/mensagens/{id}/reagir/` foi modificado para:

- ✅ Salvar reação localmente no banco de dados
- ✅ Enviar reação para o WhatsApp real via W-API
- ✅ Retornar status de ambos os envios

### 2. **Integração W-API**

```python
# Buscar instância e token
instance = WhatsappInstance.objects.filter(cliente=mensagem.cliente).first()

if instance and instance.token and mensagem.message_id:
    # Usar classe de reação da W-API
    reacao_wapi = EnviarReacao(instance.instance_id, instance.token)
    
    # Enviar para WhatsApp real
    wapi_result = reacao_wapi.enviar_reacao(
        phone=phone,
        message_id=mensagem.message_id,
        reaction=emoji,
        delay=1
    )
```

### 3. **Fluxo Completo**

1. **Usuário clica em reação** no frontend
2. **Frontend envia requisição** para `/api/mensagens/{id}/reagir/`
3. **Backend salva** reação no banco de dados
4. **Backend busca** instância e token do WhatsApp
5. **Backend envia** reação para WhatsApp real via W-API
6. **Backend retorna** status de ambos os envios
7. **Frontend atualiza** interface com nova reação
8. **Contato vê** reação no WhatsApp real

## 📋 Requisitos

### **Para funcionar corretamente:**

1. **Instância WhatsApp conectada** no painel de administração
2. **Token válido** da instância
3. **message_id** da mensagem (ID do WhatsApp)
4. **chat_id** válido (número do telefone)
5. **Cliente associado** à mensagem

### **Campos necessários:**

- `mensagem.cliente` - Cliente da mensagem
- `mensagem.chat.chat_id` - Número do telefone
- `mensagem.message_id` - ID da mensagem no WhatsApp
- `instance.instance_id` - ID da instância
- `instance.token` - Token da instância

## 🧪 Testes

### **Script de Teste:**

```bash
python test_reacao_whatsapp_real.py
```

### **Teste Manual:**

1. Configure uma instância real
2. Envie uma mensagem para um contato
3. Adicione uma reação à mensagem
4. Verifique se a reação aparece no WhatsApp do contato

## 🔍 Debug

### **Logs importantes:**

```python
# Sucesso
logger.info(f'Reação enviada para WhatsApp: emoji={emoji}, mensagem_id={mensagem.message_id}')

# Falha
logger.warning(f'Falha ao enviar reação para WhatsApp: {wapi_result["erro"]}')

# Erro geral
logger.error(f'Erro ao enviar reação para WhatsApp: {str(e)}')
```

### **Resposta da API:**

```json
{
  "sucesso": true,
  "acao": "adicionada",
  "emoji": "👍",
  "reacoes": ["👍", "❤️"],
  "wapi_enviado": true,
  "mensagem": "Reação adicionada com sucesso"
}
```

## ⚠️ Tratamento de Erros

- **Se W-API falhar**: Reação é salva apenas localmente
- **Se instância não encontrada**: Reação é salva apenas localmente
- **Se token inválido**: Reação é salva apenas localmente
- **Se message_id não existir**: Reação é salva apenas localmente

## 🚀 Status da Implementação

- ✅ **Backend Django** - Implementado
- ✅ **Integração W-API** - Implementado
- ✅ **Tratamento de erros** - Implementado
- ✅ **Logs de debug** - Implementado
- ✅ **Script de teste** - Criado
- ⏳ **Teste em produção** - Pendente

## 📞 Próximos Passos

1. **Configure uma instância real** no painel de administração
2. **Teste o envio de reações** para um contato real
3. **Verifique se as reações aparecem** no WhatsApp do contato
4. **Monitore os logs** para identificar possíveis problemas
5. **Ajuste configurações** conforme necessário 
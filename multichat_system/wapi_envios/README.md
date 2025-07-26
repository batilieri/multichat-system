# Módulos de Envio WAPI (enviosMensagensDocs)

Este diretório contém módulos prontos para envio de mensagens via WAPI, organizados por tipo de conteúdo e atualizados com as últimas funcionalidades da API WAPI.

## 📋 Módulos Disponíveis

### Mensagens Básicas
- **enviarTexto.py**: Envio de mensagens de texto
- **enviarListaOpcoes.py**: Envio de listas de opções (botões)
- **enviarEnquetes.py**: Envio de enquetes/polls

### Mídia
- **enviarImagem.py**: Envio de imagens (JPG, PNG, GIF, WebP)
- **enviarAudio.py**: Envio de áudios (MP3, OGG, WAV)
- **enviarVideo.py**: Envio de vídeos (MP4, AVI, MOV)
- **enviarGif.py**: Envio de GIFs/MP4 animados
- **enviarPTV.py**: Envio de PTV (vídeo curto/status)
- **enviarSticker.py**: Envio de stickers

### Documentos e Arquivos
- **enviarDocumento.py**: Envio de documentos (PDF, DOC, XLS, etc.)

### Interativos
- **enviarLocalizacao.py**: Envio de localização
- **enviarContato.py**: Envio de contatos

## 🚀 Padrão de Uso

Cada módulo expõe uma classe principal que deve ser instanciada com o `instance_id` e o `api_token` da WAPI. Os métodos de envio seguem o padrão:

```python
from multichat_system.wapi_envios.enviarTexto import EnviaTexto

sender = EnviaTexto(instance_id, api_token)
resposta = sender.envia_mensagem_texto(phone_number, message, delay=1)
print(resposta)
```

## 🔧 Parâmetros Gerais

### Autenticação
- `instance_id`: ID da instância WAPI (obrigatório)
- `api_token`: Token de autenticação da instância (obrigatório)

### Parâmetros de Envio
- `phone_number`: Número do telefone (formato internacional, ex: 5511999999999)
- `delay_message`: Delay em segundos entre mensagens (padrão: 1)
- `caption`: Legenda para mídia (opcional)
- `filename`: Nome do arquivo (para documentos)

## 📡 Endpoints da API WAPI

### Base URL
```
https://api.w-api.app/v1/
```

### Endpoints Principais
- **Status**: `GET /instance/status-instance`
- **Texto**: `POST /message/send-text`
- **Imagem**: `POST /message/send-image`
- **Áudio**: `POST /message/send-audio`
- **Vídeo**: `POST /message/send-video`
- **Documento**: `POST /message/send-document`
- **Localização**: `POST /message/send-location`
- **Contato**: `POST /message/send-contact`
- **Lista**: `POST /message/send-list`
- **Enquete**: `POST /message/send-poll`

## 🔄 Estrutura de Resposta

### Sucesso
```json
{
  "success": true,
  "result": {
    "messageId": "MSG123456789",
    "status": "sent",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "message": "Mensagem enviada com sucesso"
}
```

### Erro
```json
{
  "success": false,
  "error": "Descrição do erro",
  "status_code": 400,
  "details": {}
}
```

## ⚡ Funcionalidades Avançadas

### Rate Limiting
- **Mensagens**: 60 por hora por instância
- **Geral**: 100 requisições por hora por token
- **Headers informativos**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

### Validações
- Número de telefone no formato internacional
- Tamanho máximo de arquivos (16MB para mídia)
- Formatos suportados por tipo de conteúdo
- Verificação de status da instância

### Tratamento de Erros
- Timeout configurável (30s padrão)
- Retry automático para erros temporários
- Logs detalhados para debugging
- Fallback para métodos alternativos

## 🛠️ Exemplos de Uso

### Envio de Texto
```python
from multichat_system.wapi_envios.enviarTexto import EnviaTexto

sender = EnviaTexto("INSTANCE_ID", "API_TOKEN")
result = sender.envia_mensagem_texto("5511999999999", "Olá! Como você está?")
```

### Envio de Imagem
```python
from multichat_system.wapi_envios.enviarImagem import EnviaImagem

sender = EnviaImagem("INSTANCE_ID", "API_TOKEN")
result = sender.enviar("5511999999999", "/path/to/image.jpg", "Confira esta imagem!")
```

### Envio de Documento
```python
from multichat_system.wapi_envios.enviarDocumento import EnviaDocumento

sender = EnviaDocumento("INSTANCE_ID", "API_TOKEN")
result = sender.enviar("5511999999999", "/path/to/document.pdf", "Documento importante")
```

## 🔍 Monitoramento e Logs

### Logs Estruturados
- Timestamp de cada operação
- Status de sucesso/erro
- Detalhes da resposta da API
- Informações de performance

### Métricas Disponíveis
- Taxa de sucesso por tipo de mensagem
- Tempo médio de resposta
- Uso do rate limiting
- Erros por categoria

## 📚 Referência Rápida

- **Todos os módulos** utilizam os endpoints oficiais da WAPI
- **Payload e headers** seguem o padrão da documentação oficial
- **Validações robustas** para evitar erros de integração
- **Tratamento de erros** consistente em todos os módulos
- **Compatibilidade** com versões mais recentes da API

## 🔗 Links Úteis

- [Documentação Oficial WAPI](https://w-api.app/docs)
- [API Reference](https://api.w-api.app/docs)
- [Status da API](https://status.w-api.app)

---

**Dica:** Consulte o código de cada módulo para exemplos detalhados e parâmetros opcionais. Todos os módulos incluem documentação completa e exemplos de uso. 
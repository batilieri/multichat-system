# 🎵 Sistema de Áudio do WhatsApp

## 📋 Visão Geral

Este sistema permite baixar, descriptografar, converter e exibir áudios do WhatsApp no frontend. O processo inclui:

1. **Download** do áudio criptografado da API do WhatsApp
2. **Descriptografia** usando a chave de mídia fornecida
3. **Conversão** para formato MP3 usando FFmpeg
4. **Armazenamento** no sistema de arquivos
5. **Exibição** no frontend com player interativo

## 🏗️ Arquitetura

### Backend (Django)

#### `webhook/audio_processor.py`
- **WhatsAppAudioProcessor**: Classe principal para processamento de áudios
- **process_audio_from_webhook()**: Função para processar áudios via webhook

#### Funcionalidades:
- ✅ Descriptografia de áudios criptografados
- ✅ Conversão para MP3 usando FFmpeg
- ✅ Armazenamento organizado por cliente
- ✅ Validação de integridade (SHA256)
- ✅ Suporte a múltiplos formatos (OGG, OPUS, M4A)

#### `api/views.py`
- **serve_audio()**: Endpoint para servir áudios processados

#### `api/urls.py`
- **URL**: `/api/audio/<path:audio_path>/` - Serve áudios processados

### Frontend (React)

#### `Message.jsx` - AudioPlayer Component
- ✅ Player de áudio interativo
- ✅ Controles de play/pause
- ✅ Slider de progresso
- ✅ Indicador de carregamento
- ✅ Download direto
- ✅ Suporte a múltiplas fontes de áudio

## 🔧 Configuração

### Pré-requisitos

1. **FFmpeg** instalado no sistema:
   ```bash
   # Windows (com chocolatey)
   choco install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # macOS (com homebrew)
   brew install ffmpeg
   ```

2. **Dependências Python**:
   ```bash
   pip install cryptography requests
   ```

### Estrutura de Diretórios

```
multichat_system/
├── media/
│   └── audios/
│       └── {cliente_id}/
│           ├── audio_{message_id}_{timestamp}.mp3
│           └── ...
├── webhook/
│   ├── audio_processor.py
│   └── processors.py
└── api/
    ├── views.py
    └── urls.py
```

## 🚀 Como Funciona

### 1. Recebimento do Webhook

Quando um áudio é recebido via webhook:

```json
{
  "msgContent": {
    "audioMessage": {
      "url": "https://mmg.whatsapp.net/v/t62.7117-24/...",
      "mimetype": "audio/ogg; codecs=opus",
      "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
      "seconds": 8,
      "ptt": true,
      "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0=",
      "directPath": "/v/t62.7117-24/...",
      "mediaKeyTimestamp": "1754149705"
    }
  }
}
```

### 2. Processamento Automático

O sistema automaticamente:

1. **Baixa** o arquivo criptografado
2. **Verifica** a integridade (SHA256)
3. **Descriptografa** usando a chave de mídia
4. **Converte** para MP3 usando FFmpeg
5. **Salva** no sistema de arquivos
6. **Atualiza** a URL da mensagem

### 3. Exibição no Frontend

O componente `AudioPlayer` exibe:

- ✅ Botão de play/pause
- ✅ Slider de progresso
- ✅ Indicador de tempo
- ✅ Botão de download
- ✅ Indicador de carregamento
- ✅ Tratamento de erros

## 📊 Dados Processados

### Informações do Áudio

```python
{
    'file_path': 'audios/1/audio_123456_1748872244.mp3',
    'file_size': 1024000,  # bytes
    'duration': 8,          # segundos
    'ptt': True,           # Push to Talk
    'mimetype': 'audio/mpeg',
    'status': 'success'
}
```

### Campos da Mensagem

- `media_url`: URL do arquivo processado
- `media_type`: 'audio'
- `media_size`: Tamanho em bytes
- `media_caption`: Legenda (se houver)

## 🎯 Funcionalidades

### ✅ Implementadas

1. **Download automático** de áudios via webhook
2. **Descriptografia** usando chave de mídia
3. **Conversão** para MP3 com FFmpeg
4. **Armazenamento** organizado por cliente
5. **Player interativo** no frontend
6. **Download direto** dos áudios
7. **Validação de integridade** (SHA256)
8. **Tratamento de erros** robusto
9. **Suporte a múltiplos formatos**
10. **Indicadores de carregamento**

### 🔄 Processo Completo

```
Webhook → Download → Descriptografia → Conversão → Armazenamento → Frontend
   ↓         ↓            ↓              ↓            ↓            ↓
WhatsApp → Criptografado → Dados brutos → MP3 → Sistema de arquivos → Player
```

## 🧪 Testes

### Executar Testes

```bash
cd multichat_system
python ../test_audio_system.py
```

### Verificar FFmpeg

```bash
ffmpeg -version
```

### Testar Processamento

```bash
python ../test_audio_frontend.py
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **FFmpeg não encontrado**:
   - Instale o FFmpeg no sistema
   - Verifique se está no PATH

2. **Erro de descriptografia**:
   - Verifique se a chave de mídia está correta
   - Confirme se o hash SHA256 está válido

3. **Áudio não carrega no frontend**:
   - Verifique se o arquivo foi salvo corretamente
   - Confirme se a URL está acessível

4. **Erro de conversão**:
   - Verifique se o formato de entrada é suportado
   - Confirme se o FFmpeg está funcionando

### Logs

Os logs detalhados estão disponíveis em:
- `webhook/audio_processor.py` - Processamento de áudio
- `webhook/processors.py` - Integração com webhook
- `api/views.py` - Servir áudios

## 📈 Performance

### Otimizações

1. **Conversão assíncrona** (futuro)
2. **Cache de áudios** (futuro)
3. **Compressão inteligente** (futuro)
4. **Streaming de áudio** (futuro)

### Limitações Atuais

- Processamento síncrono
- Conversão para MP3 apenas
- Sem cache implementado
- Sem streaming

## 🔮 Próximos Passos

1. **Processamento assíncrono** com Celery
2. **Cache Redis** para áudios frequentes
3. **Streaming de áudio** para arquivos grandes
4. **Compressão inteligente** baseada em qualidade
5. **Suporte a mais formatos** (WAV, FLAC)
6. **Waveform visualization** no frontend
7. **Transcrição automática** de áudio para texto

## 📝 Exemplo de Uso

### Webhook de Áudio

```json
{
  "fromMe": false,
  "msgContent": {
    "audioMessage": {
      "url": "https://mmg.whatsapp.net/v/t62.7117-24/...",
      "mimetype": "audio/ogg; codecs=opus",
      "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
      "seconds": 8,
      "ptt": true,
      "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
    }
  },
  "messageId": "audio_123456"
}
```

### Resultado Processado

```json
{
  "file_path": "audios/1/audio_123456_1748872244.mp3",
  "file_size": 1024000,
  "duration": 8,
  "ptt": true,
  "mimetype": "audio/mpeg",
  "status": "success"
}
```

### URL de Acesso

```
http://localhost:8000/media/audios/1/audio_123456_1748872244.mp3
```

## ✅ Status do Sistema

- ✅ **Backend**: Implementado e funcional
- ✅ **Frontend**: Implementado e funcional
- ✅ **Processamento**: Implementado e funcional
- ✅ **Conversão**: Implementado e funcional
- ✅ **Armazenamento**: Implementado e funcional
- ✅ **Player**: Implementado e funcional
- ✅ **Download**: Implementado e funcional
- ✅ **Validação**: Implementado e funcional

**🎵 Sistema de Áudio do WhatsApp - 100% Funcional!** 
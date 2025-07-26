# 📊 Dados Mockados - MultiChat System

Esta pasta contém todos os dados mockados utilizados para desenvolvimento e testes do MultiChat System.

## 📁 Estrutura de Arquivos

```
src/data/mock/
├── index.js          # Exportações centralizadas
├── messages.js       # Dados de mensagens
├── chats.js          # Dados de chats
├── dashboard.js      # Dados do dashboard
├── notifications.js  # Dados de notificações
└── README.md         # Esta documentação
```

## 🗂️ Arquivos de Dados

### **messages.js**
- **Função**: Dados de mensagens de exemplo
- **Conteúdo**: 15 mensagens com diferentes tipos (texto, imagem, vídeo, áudio, documento, sticker)
- **Arquivos**: 7 arquivos mockados com URLs reais
- **Funcionalidades**:
  - `mockMessages` - Array de mensagens
  - `getMessagesByChat(chatId)` - Obter mensagens por chat
  - `addMessage(message)` - Adicionar nova mensagem
  - `updateMessageStatus(messageId, status)` - Atualizar status
  - `getFileStats()` - Estatísticas de arquivos
  - `getFilesByType(fileType)` - Obter arquivos por tipo
  - `getRecentFiles(limit)` - Obter arquivos recentes

### **chats.js**
- **Função**: Dados de chats de exemplo
- **Conteúdo**: 5 chats com diferentes status e atribuições
- **Funcionalidades**:
  - `mockChats` - Array de chats
  - `getAllChats()` - Obter todos os chats
  - `getChatById(chatId)` - Obter chat específico
  - `filterChats(searchQuery, filter)` - Filtrar chats
  - `updateChatAssignment(chatId, assignment)` - Atualizar atribuição
  - `updateLastMessage(chatId, message)` - Atualizar última mensagem

### **dashboard.js**
- **Função**: Dados de estatísticas do dashboard
- **Conteúdo**: Métricas, gráficos e performance de usuários
- **Funcionalidades**:
  - `mockDashboardData` - Dados completos do dashboard
  - `getDashboardData()` - Obter dados do dashboard
  - `getDashboardStats()` - Obter estatísticas resumidas
  - `getChartData()` - Obter dados para gráficos

### **notifications.js**
- **Função**: Dados de notificações
- **Conteúdo**: 5 notificações de exemplo com diferentes tipos
- **Funcionalidades**:
  - `mockNotifications` - Array de notificações
  - `getAllNotifications()` - Obter todas as notificações
  - `getUnreadNotifications()` - Obter não lidas
  - `markNotificationAsRead(notificationId)` - Marcar como lida
  - `markAllAsRead()` - Marcar todas como lidas
  - `addNotification(notification)` - Adicionar notificação
  - `getUnreadCount()` - Contar não lidas

### **index.js**
- **Função**: Arquivo central para exportações
- **Funcionalidades**:
  - Exporta todas as funções dos outros arquivos
  - `initializeMockData()` - Inicializar dados
  - `clearMockData()` - Limpar dados
  - `getMockDataSummary()` - Resumo dos dados

## 🎯 Como Usar

### **Importação Simples**
```javascript
import { mockMessages, getAllChats, getDashboardData } from '../data/mock'
```

### **Importação Específica**
```javascript
import { getMessagesByChat } from '../data/mock/messages'
import { filterChats } from '../data/mock/chats'
```

### **Inicialização**
```javascript
import { initializeMockData } from '../data/mock'

// No início da aplicação
initializeMockData()
```

## 🔧 Tipos de Dados

### **Mensagem**
```javascript
{
  id: number,
  type: 'sent' | 'received',
  tipo: 'texto' | 'imagem' | 'video' | 'audio' | 'documento' | 'sticker',
  conteudo: string,
  timestamp: string,
  sender: string,
  status: 'sent' | 'received' | 'read',
  reactions?: string[],
  isForwarded?: boolean,
  replyTo?: object,
  mediaUrl?: string,        // URL do arquivo
  filename?: string,        // Nome do arquivo
  filesize?: string,        // Tamanho (ex: "2.1 MB")
  fileType?: string,        // MIME type
  duration?: string         // Duração (para áudio/vídeo)
}
```

### **Chat**
```javascript
{
  id: number,
  chat_id: string,
  is_group: boolean,
  group_name?: string,
  profile_picture?: string,
  ultima_mensagem: object,
  atribuicao_atual: object,
  total_mensagens: number,
  sender_name: string,
  unread_count: number
}
```

### **Notificação**
```javascript
{
  id: number,
  type: 'message' | 'assignment' | 'resolved' | 'urgent' | 'system',
  title: string,
  description: string,
  time: string,
  unread: boolean
}
```

## 🎨 Layout do EmojiReactionBar

### **Posicionamento**
- **Horizontal**: Emojis alinhados horizontalmente
- **Posição**: Acima do balão de mensagem (`side="top"`)
- **Alinhamento**: Dinâmico baseado no tipo da mensagem
- **Z-index**: Alto para ficar sobre outros elementos

### **Inversão Horizontal**
- **Mensagem Recebida**: Emojis da esquerda para direita
- **Mensagem Enviada**: Emojis da direita para esquerda (invertido)
- **Alinhamento**: `align="start"` para recebidas, `align="end"` para enviadas

### **Estrutura Visual**

**Mensagem Recebida (Contato):**
```
┌─────────────────────────────────┐
│ [👍] [❤️] [😂] [😮] [😢] [😡] [+] │ ← EmojiReactionBar (normal)
└─────────────────────────────────┘
┌─────────────────────────────────┐
│        Balão de Mensagem        │
│                                 │
│        Conteúdo da msg          │
│                                 │
│ [Reações] [😊]                 │ ← Footer
└─────────────────────────────────┘
```

**Mensagem Enviada (Atendente):**
```
┌─────────────────────────────────┐
│ [+] [😡] [😢] [😮] [😂] [❤️] [👍] │ ← EmojiReactionBar (invertido)
└─────────────────────────────────┘
┌─────────────────────────────────┐
│        Balão de Mensagem        │
│                                 │
│        Conteúdo da msg          │
│                                 │
│ [Reações] [😊] [✓]             │ ← Footer
└─────────────────────────────────┘
```

### **Estrutura de Mídia com Comentário**
```
┌─────────────────────────────────┐
│        Balão de Mensagem        │
│                                 │
│ "Segue o relatório que você    │ ← Comentário da mensagem
│  pediu"                        │
│                                 │
│ [Imagem/Vídeo/Audio/Doc]       │ ← Mídia
│                                 │
│ [Reações] [😊] [✓]             │ ← Footer
└─────────────────────────────────┘
```

### **Implementação Técnica**

```javascript
// No componente Message
<PopoverContent 
  side="top" 
  align={isMe ? "end" : "start"}
  className="bg-popover border border-border p-3 rounded-xl shadow-lg"
>
  <EmojiReactionBar
    onSelect={handleAddReaction}
    onOpenFullPicker={() => setShowFullPicker(true)}
    isReversed={isMe}  // ← Chave da inversão
  />
</PopoverContent>
```

```javascript
// No componente EmojiReactionBar
const EmojiReactionBar = ({ isReversed = false }) => {
  return (
    <div className={`flex gap-1 items-center ${isReversed ? 'flex-row-reverse' : ''}`}>
      {/* Emojis */}
    </div>
  )
}
```

### **Características**
- **Animações**: Hover e tap com Framer Motion
- **Espaçamento**: Gap pequeno entre emojis
- **Tamanho**: Texto base para boa visibilidade
- **Interação**: Clique adiciona reação à mensagem
- **Responsividade**: Inversão automática baseada no tipo
- **Layout**: Imagens e vídeos com `w-auto` para evitar deslocamento
- **Comentários**: Conteúdo da mensagem exibido como comentário para mídia

## 🚀 Benefícios

1. **Desenvolvimento Rápido**: Dados prontos para uso
2. **Consistência**: Estrutura padronizada
3. **Testes**: Dados previsíveis para testes
4. **Demonstração**: Exemplos realistas
5. **Organização**: Separação clara de responsabilidades
6. **Arquivos Reais**: URLs funcionais para desenvolvimento
7. **Metadados Completos**: Informações detalhadas dos arquivos

## 📁 Sistema de Arquivos

### **Estrutura de Pastas**
```
public/files/
├── documents/     # PDF, DOCX, XLSX, PPTX
├── audio/         # MP3, WAV, OGG
├── images/        # JPG, PNG, GIF, WEBP
└── videos/        # MP4, AVI, MOV, WEBM
```

### **URLs dos Arquivos**
- **Documentos**: `/files/documents/briefing-final.pdf`
- **Áudio**: `/files/audio/mensagem-001.mp3`
- **Imagens**: `/files/images/relatorio-vendas.jpg`
- **Vídeos**: `/files/videos/demo-produto.mp4`

### **Funções de Arquivo**
```javascript
import { getFileStats, getFilesByType, getRecentFiles } from '../data/mock/messages'

// Estatísticas
const stats = getFileStats()
// { total: 7, byType: {...}, totalSize: 10.5 }

// Arquivos por tipo
const images = getFilesByType('imagem')

// Arquivos recentes
const recent = getRecentFiles(5)
```

## 🔄 Migração para API Real

Quando a API estiver pronta, basta:

1. Substituir as importações dos dados mockados
2. Implementar as chamadas para a API real
3. Manter a mesma estrutura de dados
4. Remover os arquivos mockados
5. Configurar sistema de upload de arquivos
6. Implementar CDN para arquivos estáticos

## 📝 Manutenção

- **Adicionar novos dados**: Crie novos arrays ou funções
- **Modificar estrutura**: Atualize todos os arquivos relacionados
- **Testes**: Use os dados mockados para testes unitários
- **Documentação**: Mantenha esta documentação atualizada

---

**Última Atualização**: 2025-07-12  
**Versão**: 1.0.0  
**Mantido por**: Equipe de Desenvolvimento MultiChat 
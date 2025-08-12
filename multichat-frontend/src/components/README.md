# Estrutura de Componentes do Multichat

Este diretório contém todos os componentes do sistema Multichat, organizados de forma modular e reutilizável.

## 📁 Estrutura de Diretórios

```
src/components/
├── chat/                    # Componentes específicos do chat
│   ├── ChatHeader.jsx      # Cabeçalho do chat com foto, nome e botões
│   ├── MessageInput.jsx    # Área de input de mensagem
│   ├── MessagesContainer.jsx # Container das mensagens
│   ├── PendingImagePreview.jsx # Preview de imagem pendente
│   └── index.js            # Exportações dos componentes de chat
├── modals/                  # Todos os modais do sistema
│   ├── ContactInfoModal.jsx # Modal de informações do contato
│   ├── PinnedMessagesModal.jsx # Modal de mensagens fixadas
│   ├── ForwardMessageModal.jsx # Modal de encaminhamento
│   ├── FavoritesModal.jsx  # Modal de mensagens favoritas
│   ├── MessageInfoModal.jsx # Modal de informações da mensagem
│   ├── ImageModal.jsx      # Modal de exibição de imagem
│   └── index.js            # Exportações dos modais
├── ui/                      # Componentes de UI reutilizáveis
├── ChatView.jsx            # Componente principal do chat (refatorado)
└── README.md               # Esta documentação
```

## 🔧 Componentes Extraídos

### ChatHeader
- **Responsabilidade**: Exibe o cabeçalho do chat com foto, nome, status e botões de ação
- **Props**: `chat`, `isConnected`, `favoritedMessages`, `pinnedMessages`, callbacks
- **Funcionalidades**: Foto clicável, indicador de tempo real, botões de ação

### MessageInput
- **Responsabilidade**: Área de input para digitar e enviar mensagens
- **Props**: Estados de mensagem, imagem pendente, emoji picker, callbacks
- **Funcionalidades**: Input de texto, preview de imagem, emoji picker, botão de envio

### MessagesContainer
- **Responsabilidade**: Container que exibe todas as mensagens do chat
- **Props**: Mensagens, loading, paginação, callbacks de ações
- **Funcionalidades**: Agrupamento por data, scroll infinito, ações nas mensagens

### PendingImagePreview
- **Responsabilidade**: Preview de imagem antes do envio
- **Props**: Imagem pendente, legenda, callbacks
- **Funcionalidades**: Preview da imagem, input de legenda, botão de cancelar

## 🎭 Modais

### ContactInfoModal
- **Responsabilidade**: Exibe informações detalhadas do contato
- **Funcionalidades**: Edição de nome, configurações, funções rápidas

### PinnedMessagesModal
- **Responsabilidade**: Lista de mensagens fixadas
- **Funcionalidades**: Navegação para mensagens, visualização organizada

### ForwardMessageModal
- **Responsabilidade**: Interface para encaminhar mensagens
- **Funcionalidades**: Busca de contatos, seleção múltipla, confirmação

### FavoritesModal
- **Responsabilidade**: Lista de mensagens favoritas
- **Funcionalidades**: Navegação para mensagens, visualização com timestamps

### MessageInfoModal
- **Responsabilidade**: Informações detalhadas de uma mensagem
- **Funcionalidades**: Status de entrega, visualização, reprodução

### ImageModal
- **Responsabilidade**: Exibição de imagem em tela cheia
- **Funcionalidades**: Zoom, fechamento, navegação

## 🚀 Benefícios da Refatoração

1. **Modularidade**: Cada componente tem uma responsabilidade específica
2. **Reutilização**: Componentes podem ser usados em outras partes do sistema
3. **Manutenibilidade**: Código mais organizado e fácil de manter
4. **Testabilidade**: Componentes isolados são mais fáceis de testar
5. **Performance**: Memoização e otimizações por componente
6. **Legibilidade**: Código mais limpo e compreensível

## 📝 Como Usar

### Importação
```javascript
// Importar componentes específicos
import { ChatHeader, MessageInput } from './chat';
import { ContactInfoModal, FavoritesModal } from './modals';

// Ou importar tudo
import * as ChatComponents from './chat';
import * as ModalComponents from './modals';
```

### Exemplo de Uso
```javascript
<ChatHeader
  chat={chatData}
  isConnected={true}
  favoritedMessages={favorites}
  pinnedMessages={pins}
  onOpenContactInfo={handleOpenContact}
  onOpenImageModal={handleOpenImage}
  onOpenFavoritesModal={handleOpenFavorites}
  onOpenPinsModal={handleOpenPins}
/>
```

## 🔄 Próximos Passos

1. **Testes**: Criar testes unitários para cada componente
2. **Storybook**: Implementar documentação interativa
3. **Otimizações**: Aplicar lazy loading e code splitting
4. **Acessibilidade**: Melhorar suporte a leitores de tela
5. **Internacionalização**: Preparar para múltiplos idiomas

## 📚 Recursos Adicionais

- [React Best Practices](https://react.dev/learn)
- [Component Composition Patterns](https://react.dev/learn/passing-props-to-a-component)
- [Performance Optimization](https://react.dev/learn/render-and-commit)

// Dados mockados de mensagens para desenvolvimento
export const mockMessages = [
  {
    id: 1,
    type: 'received',
    tipo: 'texto',
    conteudo: 'Oi! Já chegou em casa?',
    timestamp: '2025-07-10T15:30:00Z',
    sender: 'João Silva',
    status: 'received',
    isPinned: true,
    isFavorited: false
  },
  {
    id: 2,
    type: 'sent',
    tipo: 'texto',
    conteudo: 'Acabei de chegar sim, foi tranquilo!',
    timestamp: '2025-07-10T15:31:00Z',
    sender: 'Atendente',
    status: 'read',
    reactions: ['👌'],
    isPinned: false,
    isFavorited: true
  },
  {
    id: 3,
    type: 'received',
    tipo: 'texto',
    conteudo: 'Boa! E a reunião, como foi?',
    timestamp: '2025-07-10T15:32:00Z',
    sender: 'João Silva',
    status: 'received'
  },
  {
    id: 4,
    type: 'sent',
    tipo: 'texto',
    conteudo: 'Foi adiada pra amanhã 😅',
    timestamp: '2025-07-10T15:33:00Z',
    sender: 'Atendente',
    status: 'read',
    isForwarded: true
  },
  {
    id: 5,
    type: 'sent',
    tipo: 'imagem',
    conteudo: 'Segue o relatório que você pediu',
    mediaUrl: '/files/image.png',
    filename: 'relatorio-vendas.jpg',
    filesize: '2.1 MB',
    timestamp: '2025-07-10T15:34:00Z',
    sender: 'Atendente',
    status: 'read',
    reactions: ['📄', '✅'],
    isPinned: true
  },
  {
    id: 6,
    type: 'received',
    tipo: 'documento',
    conteudo: 'briefing-final.pdf',
    mediaUrl: '/files/document.pdf',
    filename: 'document.pdf',
    filesize: '2.5 MB',
    fileType: 'application/pdf',
    timestamp: '2025-07-10T15:35:00Z',
    sender: 'João Silva',
    status: 'received'
  },
  {
    id: 7,
    type: 'received',
    tipo: 'video',
    conteudo: 'Demonstração do produto',
    mediaUrl: '/files/video.mp4',
    filename: 'demo-produto.mp4',
    filesize: '1.2 MB',
    fileType: 'video/mp4',
    duration: '00:45',
    timestamp: '2025-07-10T15:36:00Z',
    sender: 'João Silva',
    status: 'received'
  },
  {
    id: 8,
    type: 'sent',
    tipo: 'audio',
    conteudo: 'Mensagem de áudio',
    mediaUrl: '/files/audio.m4a',
    filename: 'mensagem-001.mp3',
    filesize: '850 KB',
    fileType: 'audio/mpeg',
    duration: '00:12',
    timestamp: '2025-07-10T15:37:00Z',
    sender: 'Atendente',
    status: 'read'
  },
  {
    id: 9,
    type: 'sent',
    tipo: 'texto',
    conteudo: 'E sobre aquele projeto novo?',
    timestamp: '2025-07-10T15:38:00Z',
    sender: 'Atendente',
    status: 'read',
    replyTo: {
      id: 3,
      type: 'received',
      tipo: 'texto',
      conteudo: 'Boa! E a reunião, como foi?',
      timestamp: '2025-07-10T15:32:00Z',
      sender: 'João Silva'
    }
  },
  {
    id: 10,
    type: 'received',
    tipo: 'sticker',
    conteudo: 'Sticker enviado',
    mediaUrl: '/files/sticker.png',
    filename: 'sticker-001.webp',
    filesize: '45 KB',
    fileType: 'image/webp',
    timestamp: '2025-07-10T15:39:00Z',
    sender: 'João Silva',
    status: 'received'
  },
  {
    id: 11,
    type: 'sent',
    tipo: 'texto',
    conteudo: '😂😂',
    timestamp: '2025-07-10T15:40:00Z',
    sender: 'Atendente',
    status: 'read',
    reactions: ['❤️'],
    replyTo: {
      id: 10,
      type: 'received',
      tipo: 'sticker',
      conteudo: 'Sticker enviado',
      mediaUrl: 'https://via.placeholder.com/120x120/FF6B6B/FFFFFF?text=😄',
      timestamp: '2025-07-10T15:39:00Z',
      sender: 'João Silva'
    }
  },
  {
    id: 12,
    type: 'sent',
    tipo: 'documento',
    conteudo: 'contrato-final.docx',
    mediaUrl: '/files/documents/contrato-final.docx',
    filename: 'contrato-final.docx',
    filesize: '1.8 MB',
    fileType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    timestamp: '2025-07-10T15:41:00Z',
    sender: 'Atendente',
    status: 'sent'
  },
  {
    id: 13,
    type: 'received',
    tipo: 'texto',
    conteudo: 'Show! Falamos amanhã então.',
    timestamp: '2025-07-10T15:42:00Z',
    sender: 'João Silva',
    status: 'received'
  },
  {
    id: 14,
    type: 'received',
    tipo: 'imagem',
    conteudo: 'Foto do problema',
    mediaUrl: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop',
    filename: 'problema-001.jpg',
    filesize: '3.2 MB',
    fileType: 'image/jpeg',
    timestamp: '2025-07-10T15:43:00Z',
    sender: 'João Silva',
    status: 'received'
  },
  {
    id: 15,
    type: 'sent',
    tipo: 'audio',
    conteudo: 'Instruções de uso',
    mediaUrl: '/files/audio.m4a',
    filename: 'instrucoes-001.mp3',
    filesize: '2.1 MB',
    fileType: 'audio/mpeg',
    duration: '00:35',
    timestamp: '2025-07-10T15:44:00Z',
    sender: 'Atendente',
    status: 'read'
  }
]

// Sistema de persistência local para favoritas
const FAVORITES_STORAGE_KEY = 'multichat_favorites'
const PINNED_STORAGE_KEY = 'multichat_pinned'

// Função para carregar favoritas do localStorage
const loadFavoritesFromStorage = () => {
  try {
    const stored = localStorage.getItem(FAVORITES_STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Erro ao carregar favoritas:', error)
    return []
  }
}

// Função para salvar favoritas no localStorage
const saveFavoritesToStorage = (favorites) => {
  try {
    localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favorites))
  } catch (error) {
    console.error('Erro ao salvar favoritas:', error)
  }
}

// Função para carregar pins do localStorage
const loadPinsFromStorage = () => {
  try {
    const stored = localStorage.getItem(PINNED_STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Erro ao carregar pins:', error)
    return []
  }
}

// Função para salvar pins no localStorage
const savePinsToStorage = (pins) => {
  try {
    localStorage.setItem(PINNED_STORAGE_KEY, JSON.stringify(pins))
  } catch (error) {
    console.error('Erro ao salvar pins:', error)
  }
}

// Aplicar favoritas e pins salvos às mensagens
const applyStoredStates = () => {
  const favorites = loadFavoritesFromStorage()
  const pins = loadPinsFromStorage()
  
  mockMessages.forEach(msg => {
    msg.isFavorited = favorites.includes(msg.id)
    msg.isPinned = pins.includes(msg.id)
  })
}

// Aplicar estados salvos ao carregar
applyStoredStates()

// Função para obter mensagens por chat
export const getMessagesByChat = (chatId) => {
  // Por enquanto retorna todas as mensagens mockadas
  // No futuro, pode filtrar por chatId
  return mockMessages
}

// Função para adicionar nova mensagem
export const addMessage = (message) => {
  const newMessage = {
    id: Date.now(),
    timestamp: new Date().toISOString(),
    status: 'sent',
    isPinned: false,
    isFavorited: false,
    ...message
  }
  mockMessages.push(newMessage)
  return newMessage
}

// Função para fixar/desfixar mensagem
export const togglePinMessage = (messageId) => {
  const msg = mockMessages.find(m => m.id === messageId)
  if (msg) {
    msg.isPinned = !msg.isPinned
    
    // Atualizar localStorage
    const pins = loadPinsFromStorage()
    if (msg.isPinned) {
      if (!pins.includes(messageId)) {
        pins.push(messageId)
      }
    } else {
      const index = pins.indexOf(messageId)
      if (index > -1) {
        pins.splice(index, 1)
      }
    }
    savePinsToStorage(pins)
  }
  return msg
}

// Função para favoritar/desfavoritar mensagem
export const toggleFavoriteMessage = (messageId) => {
  const msg = mockMessages.find(m => m.id === messageId)
  if (msg) {
    msg.isFavorited = !msg.isFavorited
    
    // Atualizar localStorage
    const favorites = loadFavoritesFromStorage()
    if (msg.isFavorited) {
      if (!favorites.includes(messageId)) {
        favorites.push(messageId)
      }
    } else {
      const index = favorites.indexOf(messageId)
      if (index > -1) {
        favorites.splice(index, 1)
      }
    }
    saveFavoritesToStorage(favorites)
  }
  return msg
}

// Função para obter mensagens fixadas
export const getPinnedMessages = () => {
  return mockMessages.filter(m => m.isPinned)
}

// Função para obter mensagens favoritas
export const getFavoritedMessages = () => {
  return mockMessages.filter(m => m.isFavorited)
}

// Função para obter todas as favoritas (incluindo de outros chats)
export const getAllFavoritedMessages = () => {
  const favorites = loadFavoritesFromStorage()
  return mockMessages.filter(m => favorites.includes(m.id))
}

// Função para limpar todas as favoritas
export const clearAllFavorites = () => {
  mockMessages.forEach(msg => {
    msg.isFavorited = false
  })
  saveFavoritesToStorage([])
}

// Função para limpar todos os pins
export const clearAllPins = () => {
  mockMessages.forEach(msg => {
    msg.isPinned = false
  })
  savePinsToStorage([])
}

// Função para atualizar status de mensagem
export const updateMessageStatus = (messageId, status) => {
  const message = mockMessages.find(m => m.id === messageId)
  if (message) {
    message.status = status
  }
  return message
}

// Função para obter estatísticas de arquivos
export const getFileStats = () => {
  const files = mockMessages.filter(m => m.tipo !== 'texto')
  const stats = {
    total: files.length,
    byType: {
      imagem: files.filter(f => f.tipo === 'imagem').length,
      video: files.filter(f => f.tipo === 'video').length,
      audio: files.filter(f => f.tipo === 'audio').length,
      documento: files.filter(f => f.tipo === 'documento').length,
      sticker: files.filter(f => f.tipo === 'sticker').length
    },
    totalSize: files.reduce((acc, f) => acc + (parseFloat(f.filesize?.replace(/[^\d.]/g, '')) || 0), 0)
  }
  return stats
}

// Função para obter arquivos por tipo
export const getFilesByType = (fileType) => {
  return mockMessages.filter(m => m.tipo === fileType)
}

// Função para obter arquivos recentes
export const getRecentFiles = (limit = 10) => {
  const files = mockMessages.filter(m => m.tipo !== 'texto')
  return files
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, limit)
} 
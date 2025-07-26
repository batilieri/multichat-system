// Dados mockados de chats para desenvolvimento
export const mockChats = [
  {
    id: 1,
    chat_id: '5511999999999',
    cliente_id: 1,
    is_group: false,
    group_name: null,
    profile_picture: null,
    ultima_mensagem: {
      tipo: 'text',
      conteudo: 'Olá, preciso de ajuda com meu pedido',
      data: '2025-07-10T15:30:00Z'
    },
    atribuicao_atual: {
      status: 'aguardando',
      prioridade: 'normal',
      usuario: null,
      departamento: 'Suporte'
    },
    total_mensagens: 3,
    sender_name: 'João Silva',
    unread_count: 2
  },
  {
    id: 2,
    chat_id: '5511888888888',
    cliente_id: 1,
    is_group: false,
    group_name: null,
    profile_picture: null,
    ultima_mensagem: {
      tipo: 'text',
      conteudo: 'Obrigado pelo atendimento!',
      data: '2025-07-10T14:45:00Z'
    },
    atribuicao_atual: {
      status: 'resolvido',
      prioridade: 'normal',
      usuario: 'Maria Santos',
      departamento: 'Vendas'
    },
    total_mensagens: 8,
    sender_name: 'Ana Costa',
    unread_count: 0
  },
  {
    id: 3,
    chat_id: '5511777777777-group',
    cliente_id: 1,
    is_group: true,
    group_name: 'Suporte Técnico',
    profile_picture: null,
    ultima_mensagem: {
      tipo: 'image',
      conteudo: '[Imagem]',
      data: '2025-07-10T16:15:00Z'
    },
    atribuicao_atual: {
      status: 'em_andamento',
      prioridade: 'alta',
      usuario: 'Pedro Costa',
      departamento: 'Técnico'
    },
    total_mensagens: 15,
    sender_name: 'Grupo Suporte',
    unread_count: 1
  },
  {
    id: 4,
    chat_id: '5511666666666',
    cliente_id: 1,
    is_group: false,
    group_name: null,
    profile_picture: null,
    ultima_mensagem: {
      tipo: 'audio',
      conteudo: '[Áudio]',
      data: '2025-07-10T16:30:00Z'
    },
    atribuicao_atual: {
      status: 'aguardando',
      prioridade: 'urgente',
      usuario: null,
      departamento: 'Suporte'
    },
    total_mensagens: 5,
    sender_name: 'Carlos Oliveira',
    unread_count: 3
  },
  {
    id: 5,
    chat_id: '5511555555555',
    cliente_id: 1,
    is_group: false,
    group_name: null,
    profile_picture: null,
    ultima_mensagem: {
      tipo: 'document',
      conteudo: 'relatorio-vendas.pdf',
      data: '2025-07-10T16:45:00Z'
    },
    atribuicao_atual: {
      status: 'em_andamento',
      prioridade: 'normal',
      usuario: 'Ana Silva',
      departamento: 'Vendas'
    },
    total_mensagens: 12,
    sender_name: 'Roberto Santos',
    unread_count: 0
  }
]

// Função para obter todos os chats
export const getAllChats = () => {
  return mockChats
}

// Função para obter chat por ID
export const getChatById = (chatId) => {
  return mockChats.find(chat => chat.id === chatId)
}

// Função para filtrar chats
export const filterChats = (searchQuery, filter) => {
  return mockChats.filter(chat => {
    const matchesSearch = chat.sender_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         chat.chat_id.includes(searchQuery) ||
                         (chat.group_name && chat.group_name.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesFilter = filter === 'all' || 
                         (filter === 'waiting' && chat.atribuicao_atual?.status === 'aguardando') ||
                         (filter === 'active' && chat.atribuicao_atual?.status === 'em_andamento') ||
                         (filter === 'resolved' && chat.atribuicao_atual?.status === 'resolvido')
    
    return matchesSearch && matchesFilter
  })
}

// Função para atualizar atribuição de chat
export const updateChatAssignment = (chatId, assignment) => {
  const chat = mockChats.find(c => c.id === chatId)
  if (chat) {
    chat.atribuicao_atual = { ...chat.atribuicao_atual, ...assignment }
  }
  return chat
}

// Função para atualizar última mensagem
export const updateLastMessage = (chatId, message) => {
  const chat = mockChats.find(c => c.id === chatId)
  if (chat) {
    chat.ultima_mensagem = message
    chat.total_mensagens += 1
  }
  return chat
} 
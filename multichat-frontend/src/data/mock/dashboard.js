// Dados mockados do dashboard para desenvolvimento
export const mockDashboardData = {
  total_chats: 156,
  chats_aguardando: 12,
  chats_em_andamento: 8,
  chats_resolvidos: 136,
  total_mensagens_hoje: 342,
  mensagens_recebidas_hoje: 198,
  mensagens_enviadas_hoje: 144,
  tempo_medio_resposta: 4.2,
  usuarios_ativos: 5,
  departamentos_ativos: 3,
  mensagens_por_dia: [
    { data: '2025-07-04', total: 245 },
    { data: '2025-07-05', total: 312 },
    { data: '2025-07-06', total: 189 },
    { data: '2025-07-07', total: 267 },
    { data: '2025-07-08', total: 298 },
    { data: '2025-07-09', total: 334 },
    { data: '2025-07-10', total: 342 }
  ],
  chats_por_status: {
    aguardando: 12,
    em_andamento: 8,
    resolvido: 136
  },
  mensagens_por_tipo: {
    text: 245,
    image: 67,
    document: 23,
    audio: 7
  },
  performance_usuarios: [
    { 
      nome: 'João Silva', 
      total_chats: 45, 
      chats_resolvidos: 42, 
      taxa_resolucao: 93.3 
    },
    { 
      nome: 'Maria Santos', 
      total_chats: 38, 
      chats_resolvidos: 35, 
      taxa_resolucao: 92.1 
    },
    { 
      nome: 'Pedro Costa', 
      total_chats: 32, 
      chats_resolvidos: 28, 
      taxa_resolucao: 87.5 
    }
  ]
}

// Função para obter dados do dashboard
export const getDashboardData = () => {
  return mockDashboardData
}

// Função para obter estatísticas resumidas
export const getDashboardStats = () => {
  const { 
    total_chats, 
    chats_aguardando, 
    chats_em_andamento, 
    chats_resolvidos,
    total_mensagens_hoje,
    tempo_medio_resposta,
    usuarios_ativos
  } = mockDashboardData

  return [
    {
      title: 'Total de Chats',
      value: total_chats,
      change: 12,
      icon: 'MessageCircle',
      color: 'blue'
    },
    {
      title: 'Aguardando',
      value: chats_aguardando,
      change: -5,
      icon: 'Clock',
      color: 'orange'
    },
    {
      title: 'Em Andamento',
      value: chats_em_andamento,
      change: 8,
      icon: 'Activity',
      color: 'blue'
    },
    {
      title: 'Resolvidos',
      value: chats_resolvidos,
      change: 15,
      icon: 'CheckCircle',
      color: 'green'
    },
    {
      title: 'Mensagens Hoje',
      value: total_mensagens_hoje,
      change: 23,
      icon: 'MessageCircle',
      color: 'purple'
    },
    {
      title: 'Tempo Médio',
      value: `${tempo_medio_resposta} min`,
      change: -0.5,
      icon: 'Clock',
      color: 'yellow'
    },
    {
      title: 'Usuários Ativos',
      value: usuarios_ativos,
      change: 0,
      icon: 'Users',
      color: 'indigo'
    }
  ]
}

// Função para obter dados de gráficos
export const getChartData = () => {
  return {
    mensagensPorDia: mockDashboardData.mensagens_por_dia,
    chatsPorStatus: mockDashboardData.chats_por_status,
    mensagensPorTipo: mockDashboardData.mensagens_por_tipo,
    performanceUsuarios: mockDashboardData.performance_usuarios
  }
} 
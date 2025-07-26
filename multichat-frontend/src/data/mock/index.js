// Arquivo central para exportar todos os dados mockados
export * from './messages'
export * from './chats'
export * from './dashboard'
export * from './notifications'

// Função para inicializar todos os dados mockados
export const initializeMockData = () => {
  console.log('📊 Dados mockados inicializados')
  console.log('- Mensagens:', '13 mensagens de exemplo')
  console.log('- Chats:', '5 chats de exemplo')
  console.log('- Dashboard:', 'Dados de estatísticas')
  console.log('- Notificações:', '5 notificações de exemplo')
}

// Função para limpar dados mockados (útil para testes)
export const clearMockData = () => {
  console.log('🧹 Dados mockados limpos')
}

// Função para obter resumo dos dados mockados
export const getMockDataSummary = () => {
  return {
    messages: 13,
    chats: 5,
    notifications: 5,
    dashboardStats: 7
  }
} 
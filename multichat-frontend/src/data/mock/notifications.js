// Dados mockados de notificações para desenvolvimento
export const mockNotifications = [
  {
    id: 1,
    type: 'message',
    title: 'Nova mensagem',
    description: 'João Silva enviou uma mensagem',
    time: '2 min atrás',
    unread: true
  },
  {
    id: 2,
    type: 'assignment',
    title: 'Chat atribuído',
    description: 'Novo chat foi atribuído para você',
    time: '5 min atrás',
    unread: true
  },
  {
    id: 3,
    type: 'resolved',
    title: 'Chat resolvido',
    description: 'Chat #1234 foi marcado como resolvido',
    time: '10 min atrás',
    unread: false
  },
  {
    id: 4,
    type: 'urgent',
    title: 'Chat urgente',
    description: 'Chat #5678 marcado como urgente',
    time: '15 min atrás',
    unread: true
  },
  {
    id: 5,
    type: 'system',
    title: 'Manutenção programada',
    description: 'Sistema ficará indisponível das 2h às 4h',
    time: '1 hora atrás',
    unread: false
  }
]

// Função para obter todas as notificações
export const getAllNotifications = () => {
  return mockNotifications
}

// Função para obter notificações não lidas
export const getUnreadNotifications = () => {
  return mockNotifications.filter(notification => notification.unread)
}

// Função para marcar notificação como lida
export const markNotificationAsRead = (notificationId) => {
  const notification = mockNotifications.find(n => n.id === notificationId)
  if (notification) {
    notification.unread = false
  }
  return notification
}

// Função para marcar todas como lidas
export const markAllAsRead = () => {
  mockNotifications.forEach(notification => {
    notification.unread = false
  })
}

// Função para adicionar nova notificação
export const addNotification = (notification) => {
  const newNotification = {
    id: Date.now(),
    time: 'agora',
    unread: true,
    ...notification
  }
  mockNotifications.unshift(newNotification)
  return newNotification
}

// Função para obter contagem de não lidas
export const getUnreadCount = () => {
  return mockNotifications.filter(n => n.unread).length
} 
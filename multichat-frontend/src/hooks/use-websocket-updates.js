import { useEffect, useRef, useCallback } from 'react'
import webSocketService from '../services/websocket-service'
import { useAuth } from '../contexts/AuthContext'

/**
 * Hook otimizado que usa WebSocket quando disponível e fallback para polling
 */
export const useWebSocketUpdates = (chatId, onNewMessage, onChatUpdate) => {
  const { apiRequest } = useAuth()
  const pollingRef = useRef(null)
  const lastCheckRef = useRef(new Date().toISOString())
  const isPollingRef = useRef(false)

  // Função de fallback para polling
  const checkForUpdates = useCallback(async () => {
    if (isPollingRef.current) return
    
    isPollingRef.current = true
    try {
      const response = await apiRequest(`/api/chats/check-updates/?last_check=${lastCheckRef.current}&chat_id=${chatId}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.has_updates && data.updates && Array.isArray(data.updates)) {
        data.updates.forEach(update => {
          if (update.type === 'new_message' && update.message) {
            onNewMessage?.(update.message)
          } else if (update.type === 'chat_updated') {
            onChatUpdate?.(update)
          }
        })
        
        lastCheckRef.current = data.timestamp
      }
    } catch (error) {
      console.error('❌ Erro no polling de fallback:', error)
    } finally {
      isPollingRef.current = false
    }
  }, [apiRequest, chatId, onNewMessage, onChatUpdate])

  // Configurar WebSocket
  useEffect(() => {
    if (!chatId) return

    console.log('🔌 Configurando WebSocket para chat:', chatId)
    
    // Tentar conectar WebSocket
    webSocketService.connect(chatId)
    
    // Registrar callbacks
    webSocketService.subscribe('message_update', onNewMessage)
    webSocketService.subscribe('chat_update', onChatUpdate)
    
    // Iniciar polling de fallback se WebSocket não estiver disponível
    const startPolling = () => {
      if (!webSocketService.isWebSocketAvailable()) {
        console.log('🔄 WebSocket não disponível, iniciando polling de fallback')
        pollingRef.current = setInterval(checkForUpdates, 5000)
      }
    }
    
    // Verificar após um delay se WebSocket está funcionando
    const checkWebSocketTimeout = setTimeout(startPolling, 3000)
    
    return () => {
      clearTimeout(checkWebSocketTimeout)
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
      }
      webSocketService.unsubscribe('message_update')
      webSocketService.unsubscribe('chat_update')
    }
  }, [chatId, onNewMessage, onChatUpdate, checkForUpdates])

  // Retornar status de conexão
  return {
    isConnected: webSocketService.isWebSocketAvailable(),
    isWebSocket: webSocketService.isWebSocketAvailable(),
    isPolling: !webSocketService.isWebSocketAvailable() && pollingRef.current !== null
  }
} 
import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'

/**
 * Hook principal para gerenciar atualizações em tempo real dos chats
 */
export const useRealtimeUpdates = () => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)
  const { apiRequest } = useAuth()
  const pollingRef = useRef(null)
  const lastCheckRef = useRef(new Date().toISOString())
  const callbacksRef = useRef(new Map())
  const globalCallbacksRef = useRef([])
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  // Função para verificar atualizações
  const checkForUpdates = useCallback(async () => {
    try {
      const response = await apiRequest(`/api/chats/check-updates/?last_check=${lastCheckRef.current}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('📡 Atualizações recebidas:', data)

      if (data.updates && Array.isArray(data.updates)) {
        // Processar cada atualização de forma mais eficiente
        data.updates.forEach(update => {
          // Verificar se é uma atualização global
          if (update.type === 'global_new_message') {
            console.log('🌐 Atualização global recebida:', update)
            // Executar callbacks globais
            globalCallbacksRef.current.forEach(callback => {
              try {
                callback(update)
              } catch (error) {
                console.error('❌ Erro ao executar callback global:', error)
              }
            })
          } else if (update.type === 'new_message') {
            // Atualização específica de nova mensagem
            console.log('📨 Nova mensagem recebida:', update)
            const callbacks = callbacksRef.current.get(update.chat_id) || []
            callbacks.forEach(callback => {
              try {
                callback(update)
              } catch (error) {
                console.error('❌ Erro ao executar callback:', error)
              }
            })
          } else if (update.type === 'chat_updated') {
            // Atualização de chat (sem nova mensagem)
            console.log('🔄 Chat atualizado:', update)
            const callbacks = callbacksRef.current.get(update.chat_id) || []
            callbacks.forEach(callback => {
              try {
                callback(update)
              } catch (error) {
                console.error('❌ Erro ao executar callback:', error)
              }
            })
          }
        })

        setLastUpdate(data.timestamp)
        lastCheckRef.current = data.timestamp
      }

      setIsConnected(true)
      reconnectAttempts.current = 0 // Reset tentativas de reconexão
    } catch (error) {
      console.error('❌ Erro ao verificar atualizações:', error)
      setIsConnected(false)
      
      // Tentar reconectar com exponential backoff
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
        console.log(`🔄 Tentativa de reconexão ${reconnectAttempts.current}/${maxReconnectAttempts} em ${delay}ms`)
        
        setTimeout(() => {
          if (pollingRef.current) {
            checkForUpdates()
          }
        }, delay)
      }
    }
  }, [apiRequest])

  // Função para conectar
  const connect = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
    }

    console.log('🔌 Conectando ao sistema de tempo real...')
    
    // Verificação inicial
    checkForUpdates()
    
    // Iniciar polling a cada 3 segundos
    pollingRef.current = setInterval(checkForUpdates, 3000)
    
    setIsConnected(true)
  }, [checkForUpdates])

  // Função para desconectar
  const disconnect = useCallback(() => {
    console.log('🔌 Desconectando do sistema de tempo real...')
    
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    
    setIsConnected(false)
    reconnectAttempts.current = 0
  }, [])

  // Função para registrar callbacks específicos de chat
  const registerCallbacks = useCallback((chatId, callbacks) => {
    console.log(`🎯 Registrando callbacks para chat: ${chatId}`)
    callbacksRef.current.set(chatId, callbacks)
  }, [])

  // Função para remover callbacks específicos de chat
  const unregisterCallbacks = useCallback((chatId) => {
    console.log(`🗑️ Removendo callbacks para chat: ${chatId}`)
    callbacksRef.current.delete(chatId)
  }, [])

  // Função para registrar callbacks globais
  const registerGlobalCallback = useCallback((callback) => {
    console.log('🌐 Registrando callback global')
    globalCallbacksRef.current.push(callback)
  }, [])

  // Função para remover callbacks globais
  const unregisterGlobalCallback = useCallback((callback) => {
    console.log('🗑️ Removendo callback global')
    globalCallbacksRef.current = globalCallbacksRef.current.filter(cb => cb !== callback)
  }, [])

  // Limpeza na desmontagem
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    isConnected,
    lastUpdate,
    connect,
    disconnect,
    registerCallbacks,
    unregisterCallbacks,
    registerGlobalCallback,
    unregisterGlobalCallback
  }
}

/**
 * Hook específico para atualizações de chat
 */
export const useChatUpdates = (chatId, onNewMessage, onChatUpdate) => {
  const { registerCallbacks, unregisterCallbacks, isConnected } = useRealtimeUpdates()

  useEffect(() => {
    if (!chatId) return

    console.log(`🎯 Configurando atualizações para chat: ${chatId}`)

    const callbacks = {
      new_message: (update) => {
        console.log('📨 Nova mensagem recebida:', update)
        if (onNewMessage && update.message) {
          onNewMessage(update.message)
        }
      },
      chat_updated: (update) => {
        console.log('🔄 Chat atualizado:', update)
        if (onChatUpdate) {
          onChatUpdate(update)
        }
      }
    }

    registerCallbacks(chatId, callbacks)

    return () => {
      unregisterCallbacks(chatId)
    }
  }, [chatId, onNewMessage, onChatUpdate, registerCallbacks, unregisterCallbacks])

  return { isConnected }
}

/**
 * Hook para atualizações globais (afeta todos os chats)
 */
export const useGlobalUpdates = (onGlobalUpdate) => {
  const { registerGlobalCallback, unregisterGlobalCallback, isConnected } = useRealtimeUpdates()

  useEffect(() => {
    console.log('🌐 Configurando atualizações globais')

    const globalCallback = (update) => {
      console.log('🌐 Atualização global recebida:', update)
      if (onGlobalUpdate) {
        onGlobalUpdate(update)
      }
    }

    registerGlobalCallback(globalCallback)

    return () => {
      unregisterGlobalCallback(globalCallback)
    }
  }, [onGlobalUpdate, registerGlobalCallback, unregisterGlobalCallback])

  return { isConnected }
}

/**
 * Hook para atualizações da lista de chats
 */
export const useChatListUpdates = (onChatUpdate) => {
  const { registerCallbacks, unregisterCallbacks } = useRealtimeUpdates()

  useEffect(() => {
    console.log('📋 Configurando atualizações da lista de chats')

    const callbacks = {
      chat_updated: (update) => {
        console.log('🔄 Chat da lista atualizado:', update)
        if (onChatUpdate) {
          onChatUpdate(update.chat_id, update)
        }
      },
      global_new_message: (update) => {
        console.log('🌐 Nova mensagem global para lista de chats:', update)
        if (onChatUpdate) {
          // Atualizar a lista de chats com a nova mensagem
          onChatUpdate(update.data.chat_id, {
            type: 'global_new_message',
            last_message: update.data.message,
            timestamp: update.data.timestamp
          })
        }
      }
    }

    // Registrar para todos os chats (chatId = 'all')
    registerCallbacks('all', callbacks)

    return () => {
      unregisterCallbacks('all')
    }
  }, [onChatUpdate, registerCallbacks, unregisterCallbacks])
} 
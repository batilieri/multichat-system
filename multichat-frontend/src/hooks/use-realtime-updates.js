import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'

/**
 * Cache inteligente para mensagens
 */
class MessageCache {
  constructor() {
    this.cache = new Map()
    this.maxSize = 1000 // Limite de mensagens em cache
  }
  
  addMessage(chatId, message) {
    if (!this.cache.has(chatId)) {
      this.cache.set(chatId, [])
    }
    
    const messages = this.cache.get(chatId)
    
    // Evita duplicatas
    if (!messages.find(msg => msg.id === message.id)) {
      messages.push(message)
      
      // Limita tamanho do cache
      if (messages.length > this.maxSize) {
        messages.shift() // Remove mensagem mais antiga
      }
    }
  }
  
  getMessages(chatId) {
    return this.cache.get(chatId) || []
  }

  clearChat(chatId) {
    this.cache.delete(chatId)
  }
}

// Instância global do cache
const messageCache = new MessageCache()

/**
 * Hook principal para gerenciar atualizações em tempo real dos chats - OTIMIZADO
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
  const isPollingRef = useRef(false) // Previne requisições simultâneas
  const hasActiveWebhookRef = useRef(false) // Controle de webhook ativo

  // Função para desconectar (sem dependências)
  const disconnect = useCallback(() => {
    console.log('🔌 Desconectando do sistema de tempo real...')
    
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    
    setIsConnected(false)
    reconnectAttempts.current = 0
  }, [])

  // Função para verificar atualizações (depende de disconnect)
  const checkForUpdates = useCallback(async () => {
    if (isPollingRef.current) return
    
    isPollingRef.current = true
    try {
      const response = await apiRequest(`/api/chats/check-updates/?last_check=${lastCheckRef.current}`)
      
      if (!response.ok) {
        // Se for erro 401, tentar renovar token e reconectar
        if (response.status === 401) {
          console.log('🔐 Token expirado, tentando renovar...')
          // A função apiRequest já deve ter tentado renovar o token
          // Se ainda falhou, fazer logout e parar polling
          if (response.status === 401) {
            console.error('❌ Falha na autenticação após renovação, parando sistema de tempo real')
            disconnect()
            return
          }
        }
        
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('📡 Atualizações recebidas:', data)

      if (data.has_updates && data.updates && Array.isArray(data.updates)) {
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
            const chatId = update.chat_id || update.chat?.id
            if (chatId && callbacksRef.current.has(chatId)) {
              const callbacks = callbacksRef.current.get(chatId)
              if (Array.isArray(callbacks)) {
                callbacks.forEach(callback => {
                  try {
                    callback(update)
                  } catch (error) {
                    console.error('❌ Erro ao executar callback:', error)
                  }
                })
              } else {
                console.warn('⚠️ Callbacks não é um array:', callbacks)
              }
            }
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
      
      // Se for erro de autenticação, parar polling
      if (error.message && error.message.includes('401')) {
        console.error('🔐 Erro de autenticação, parando sistema de tempo real')
        disconnect()
        return
      }
      
      // Tentar reconectar com exponential backoff apenas para outros tipos de erro
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
        console.log(`🔄 Tentativa de reconexão ${reconnectAttempts.current}/${maxReconnectAttempts} em ${delay}ms`)
        
        setTimeout(() => {
          if (pollingRef.current) {
            checkForUpdates()
          }
        }, delay)
      } else {
        console.error('❌ Máximo de tentativas de reconexão atingido, parando sistema de tempo real')
        disconnect()
      }
    } finally {
      isPollingRef.current = false
    }
  }, [apiRequest, disconnect])

  // Função para conectar (depende de checkForUpdates)
  const connect = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
    }

    console.log('🔌 Conectando ao sistema de tempo real...')
    
    // Verificação inicial
    checkForUpdates()
    
    // Iniciar polling a cada 3 segundos
    pollingRef.current = setInterval(() => {
      if (!hasActiveWebhookRef.current) {
        checkForUpdates()
      }
    }, 3000)
    
    setIsConnected(true)
  }, [checkForUpdates])

  // Iniciar polling quando o hook é montado - OTIMIZADO
  useEffect(() => {
    console.log('🔌 Iniciando sistema de tempo real...')
    pollingRef.current = true
    lastCheckRef.current = new Date(Date.now() - 60000).toISOString() // 1 minuto atrás
    
    // Primeira verificação imediata
    checkForUpdates()
    
    // Configurar polling a cada 3 segundos - OTIMIZADO
    const interval = setInterval(() => {
      if (pollingRef.current && !hasActiveWebhookRef.current) {
        checkForUpdates()
      }
    }, 3000) // 3 segundos

    return () => {
      console.log('🔌 Parando sistema de tempo real...')
      pollingRef.current = false
      clearInterval(interval)
    }
  }, [checkForUpdates])

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

  // Função para controlar webhook ativo
  const setWebhookActive = useCallback((active) => {
    hasActiveWebhookRef.current = active
    console.log(`🔌 Webhook ${active ? 'ativado' : 'desativado'}`)
  }, [])

  // Função para obter mensagens do cache
  const getCachedMessages = useCallback((chatId) => {
    return messageCache.getMessages(chatId)
  }, [])

  // Função para limpar cache de um chat
  const clearChatCache = useCallback((chatId) => {
    messageCache.clearChat(chatId)
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
    unregisterGlobalCallback,
    setWebhookActive,
    getCachedMessages,
    clearChatCache
  }
}

/**
 * Hook específico para atualizações de chat - OTIMIZADO
 */
export const useChatUpdates = (chatId, onNewMessage, onChatUpdate) => {
  const { 
    registerCallbacks, 
    unregisterCallbacks, 
    isConnected,
    getCachedMessages,
    clearChatCache
  } = useRealtimeUpdates()

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

  return { 
    isConnected,
    getCachedMessages: () => getCachedMessages(chatId),
    clearChatCache: () => clearChatCache(chatId)
  }
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
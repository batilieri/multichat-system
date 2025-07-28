import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Filter,
  Clock,
  MessageCircle,
  User,
  Users,
  MoreVertical,
  Star,
  Archive,
  Tag
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useChatListUpdates, useGlobalUpdates } from '../hooks/use-realtime-updates'

// Componente de skeleton para loading
const ChatSkeleton = () => (
  <div className="flex items-center space-x-3 p-3 animate-pulse">
    <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
    <div className="flex-1 space-y-2">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
    </div>
  </div>
)

const ChatList = ({ selectedChat, onSelectChat }) => {
  const [chats, setChats] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all') // all, waiting, active, resolved
  const { apiRequest } = useAuth()
  const [isRealtimeConnected, setIsRealtimeConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)
  // REMOVIDO: autoRefreshEnabled - agora tudo é automático

  // Removido dados mockados - usando apenas dados reais da API

  // Função para lidar com atualizações globais - MELHORADA
  const handleGlobalUpdate = useCallback((update) => {
    console.log('🌐 Atualização global recebida no ChatList:', update)
    
    if (update.type === 'global_new_message') {
      const { chat_id, chat_name, sender_name, timestamp, message } = update.data
      
      // Atualizar apenas o chat específico na lista (sem recarregar tudo)
      setChats(prevChats => {
        return prevChats.map(chat => {
          if (chat.chat_id === chat_id) {
            // Atualizar apenas o chat que recebeu a nova mensagem
            return {
              ...chat,
              last_message_at: timestamp,
              total_mensagens: (chat.total_mensagens || 0) + 1,
              ultima_mensagem: {
                tipo: message.type,
                conteudo: message.content,
                data: timestamp,
                sender: sender_name
              }
            }
          }
          return chat
        })
      })
      
      setLastUpdate(new Date().toISOString())
      console.log(`✅ Chat ${chat_id} atualizado com nova mensagem`)
    }
  }, [])

  // Função para lidar com atualizações específicas de chat
  const handleChatUpdate = useCallback((chatId, chatData) => {
    console.log('🔄 Chat atualizado em tempo real:', chatId, chatData)
    
    if (chatData.type === 'new_message') {
      // Nova mensagem recebida
      setChats(prevChats => {
        return prevChats.map(chat => {
          if (chat.chat_id === chatId) {
            return {
              ...chat,
              last_message_at: chatData.message.timestamp,
              total_mensagens: (chat.total_mensagens || 0) + 1,
              ultima_mensagem: {
                tipo: chatData.message.type,
                conteudo: chatData.message.content,
                data: chatData.message.timestamp,
                sender: chatData.message.sender
              }
            }
          }
          return chat
        })
      })
    } else if (chatData.type === 'chat_updated') {
      // Chat atualizado (sem nova mensagem)
      setChats(prevChats => {
        return prevChats.map(chat => {
          if (chat.chat_id === chatId) {
            return {
              ...chat,
              last_message_at: chatData.last_message_at,
              total_mensagens: chatData.message_count,
              // Manter última mensagem se não houver nova
              ultima_mensagem: chat.ultima_mensagem || {
                tipo: 'text',
                conteudo: 'Chat atualizado',
                data: chatData.last_message_at,
                sender: 'Sistema'
              }
            }
          }
          return chat
        })
      })
    }
    
    setLastUpdate(new Date().toISOString())
  }, [])

  // Função para recarregar chats automaticamente - REMOVIDO AUTO-REFRESH
  const handleAutoRefresh = useCallback(() => {
    // Removido auto-refresh para evitar piscamento
    // A atualização agora é feita apenas quando há nova mensagem
  }, [])

  // Usar hook de atualizações em tempo real para lista de chats
  useChatListUpdates(handleChatUpdate)
  
  // Usar hook de atualizações globais
  useGlobalUpdates(handleGlobalUpdate)

  // Sistema de auto-refresh REMOVIDO - agora só atualiza quando há nova mensagem
  // useEffect(() => {
  //   if (!autoRefreshEnabled) return
  //   const interval = setInterval(handleAutoRefresh, 10000)
  //   return () => clearInterval(interval)
  // }, [handleAutoRefresh, autoRefreshEnabled])

  // OTIMIZADO: loadChats com timeout e melhor tratamento de erro
  const loadChats = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('🔍 Carregando chats...')
      
      const response = await apiRequest('/api/chats/')
      console.log('🔍 Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Erro detalhado:', errorText)
        throw new Error(`HTTP ${response.status}: ${response.statusText}\n${errorText}`)
      }
      
      // Ler o corpo como texto e tentar parsear como JSON
      const responseText = await response.text()
      let data
      try {
        data = JSON.parse(responseText)
      } catch (jsonError) {
        console.error('❌ Resposta não é JSON. Conteúdo recebido:', responseText)
        throw new Error('A resposta da API não é um JSON válido.\nConteúdo recebido:\n' + responseText)
      }
      console.log('🔍 Dados recebidos:', data)
      
      // Corrigir para sempre processar um array
      // W-API retorna em 'chats', não 'results'
      const chatsArray = Array.isArray(data.chats) ? data.chats : Array.isArray(data.results) ? data.results : Array.isArray(data) ? data : [];
      
      // Transformação para garantir campos obrigatórios - OTIMIZADA
      const transformedChats = chatsArray.map(chat => ({
        ...chat,
        ultima_mensagem: chat.ultima_mensagem || {
          tipo: 'text',
          conteudo: 'Nenhuma mensagem ainda',
          data: chat.data_inicio || new Date().toISOString(),
          sender: 'Sistema'
        },
        last_message_at: chat.last_message_at || chat.data_inicio || new Date().toISOString(),
        total_mensagens: chat.total_mensagens || 0,
        status: chat.status || 'active',
        prioridade: chat.prioridade || 'medium'
      }))
      
      setChats(transformedChats)
      setLastUpdate(new Date().toISOString())
      console.log(`✅ ${transformedChats.length} chats carregados com sucesso`)
      
    } catch (error) {
      console.error('❌ Erro ao carregar chats:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }, [apiRequest])

  useEffect(() => {
    loadChats()
  }, [loadChats])

  // OTIMIZADO: Filtrar chats com useMemo
  const filteredChats = useMemo(() => {
    if (!chats.length) return []
    
    switch (filter) {
      case 'waiting':
        return chats.filter(chat => chat.status === 'pending')
      case 'active':
        return chats.filter(chat => chat.status === 'active')
      case 'resolved':
        return chats.filter(chat => chat.status === 'closed')
      default:
        return chats
    }
  }, [chats, filter])

  // OTIMIZADO: Ordenar chats com useMemo
  const sortedChats = useMemo(() => {
    return [...filteredChats].sort((a, b) => {
      const dateA = new Date(a.last_message_at || a.data_inicio || 0)
      const dateB = new Date(b.last_message_at || b.data_inicio || 0)
      return dateB - dateA
    })
  }, [filteredChats])

  // Funções utilitárias - OTIMIZADAS
  const getStatusColor = useCallback((status) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'pending': return 'bg-yellow-500'
      case 'closed': return 'bg-gray-500'
      default: return 'bg-gray-400'
    }
  }, [])

  const getPriorityColor = useCallback((prioridade) => {
    switch (prioridade) {
      case 'high': return 'text-red-500'
      case 'medium': return 'text-yellow-500'
      case 'low': return 'text-green-500'
      default: return 'text-gray-500'
    }
  }, [])

  const formatTime = useCallback((dateString) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now - date) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    } else if (diffInHours < 48) {
      return 'Ontem'
    } else {
      return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    }
  }, [])

  // Renderizar skeleton loading
  if (loading) {
    return (
      <div className="h-full overflow-y-auto">
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Chats</h2>
            <div className="w-6 h-6 bg-gray-200 rounded animate-pulse"></div>
          </div>
          <div className="flex space-x-2">
            {['all', 'waiting', 'active', 'resolved'].map(filter => (
              <div key={filter} className="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        </div>
        <div className="space-y-1">
          {Array.from({ length: 10 }).map((_, i) => (
            <ChatSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  // Renderizar erro
  if (error) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-red-500 mb-2">❌ Erro ao carregar chats</div>
          <div className="text-sm text-muted-foreground mb-4">{error}</div>
          <button 
            onClick={loadChats}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header com filtros */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-semibold">Chats</h2>
            {/* Indicador de atualização automática - SEM ÍCONE DE SINCRONIZAÇÃO */}
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-green-600 font-medium">Tempo real</span>
            </div>
          </div>
          
          {/* Contador de chats */}
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Filter className="w-4 h-4" />
            <span>
              {sortedChats.length} {sortedChats.length === 1 ? 'chat' : 'chats'}
            </span>
            {lastUpdate && (
              <span className="text-xs">
                • Atualizado {formatTime(lastUpdate)}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Lista de chats */}
      <div className="flex-1 overflow-y-auto">
        {sortedChats.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Nenhum chat encontrado</p>
              <p className="text-sm">Os chats aparecerão aqui quando houver mensagens</p>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {sortedChats.map((chat) => (
              <div
                key={chat.chat_id || chat.id}
                onClick={() => onSelectChat(chat)}
                className={`
                  flex items-center space-x-3 p-3 cursor-pointer transition-colors
                  ${selectedChat?.chat_id === chat.chat_id
                    ? 'bg-primary/10 border-r-2 border-primary'
                    : 'hover:bg-muted/50'
                  }
                `}
              >
                {/* Avatar */}
                <div className="relative">
                  {(chat.foto_perfil || chat.profile_picture) ? (
                    <div className="w-10 h-10 rounded-full overflow-hidden">
                      <img
                        src={chat.foto_perfil || chat.profile_picture}
                        alt={chat.contact_name || chat.sender_name || 'Foto do contato'}
                        className="h-full w-full object-cover"
                        onError={(e) => {
                          // Fallback para avatar com inicial se a imagem falhar
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-primary-foreground font-semibold hidden">
                        {chat.is_group ? (
                          <Users className="w-5 h-5" />
                        ) : (
                          <span>{chat.contact_name?.charAt(0)?.toUpperCase() || '?'}</span>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-primary-foreground font-semibold">
                      {chat.is_group ? (
                        <Users className="w-5 h-5" />
                      ) : (
                        <span>{chat.contact_name?.charAt(0)?.toUpperCase() || '?'}</span>
                      )}
                    </div>
                  )}
                  <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-background ${getStatusColor(chat.status)}`}></div>
                </div>

                {/* Informações do chat */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-sm truncate">
                      {chat.contact_name || chat.sender_name || `Chat ${chat.id}`}
                    </h3>
                    <span className="text-xs text-muted-foreground">
                      {formatTime(chat.last_message_at)}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-xs text-muted-foreground truncate">
                      {chat.ultima_mensagem?.conteudo || 'Nenhuma mensagem ainda'}
                    </p>
                    {chat.unread_count > 0 && (
                      <span className="bg-primary text-primary-foreground text-xs px-2 py-0.5 rounded-full min-w-[20px] text-center">
                        {chat.unread_count}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatList


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
import { useChatListUpdates } from '../hooks/use-realtime-updates'

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

  // Removido dados mockados - usando apenas dados reais da API

  // Função para atualizar chat em tempo real - OTIMIZADA
  const handleChatUpdate = useCallback((chatId, chatData) => {
    console.log('🔄 Chat atualizado em tempo real:', chatId, chatData)
    
    setChats(prevChats => {
      return prevChats.map(chat => {
        if (chat.chat_id === chatId) {
          return {
            ...chat,
            last_message_at: chatData.last_message_at,
            total_mensagens: chatData.message_count,
            // Atualizar última mensagem se necessário
            ultima_mensagem: {
              ...chat.ultima_mensagem,
              data: chatData.last_message_at
            }
          }
        }
        return chat
      })
    })
  }, [])

  // Usar hook de atualizações em tempo real para lista de chats
  useChatListUpdates(handleChatUpdate)

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
          data: chat.data_inicio || new Date().toISOString()
        },
        total_mensagens: chat.total_mensagens ?? 0,
        unread_count: chat.unread_count ?? 0,
        // sender_name será o número de telefone (chat_id)
        sender_name: chat.sender_name || chat.chat_id || `Chat ${chat.id}`,
        // contact_name será o nome do contato
        contact_name: chat.contact_name || chat.chat_name || chat.sender_name || chat.cliente_nome || `Chat ${chat.id}`,
        group_name: chat.group_name || null,
        is_group: chat.is_group || false,
        chat_name: chat.contact_name || chat.chat_name || chat.sender_name || chat.cliente_nome || `Chat ${chat.id}` // Para garantir compatibilidade
      }))
      
      console.log('✅ Chats carregados:', transformedChats.length)
      setChats(transformedChats)
      
    } catch (error) {
      console.error('❌ Erro ao carregar chats:', error)
      setError(error.message)
      // Em caso de erro, mostrar lista vazia mas não quebrar a aplicação
      setChats([])
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
          <h2 className="text-lg font-semibold">Chats</h2>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {sortedChats.length} {sortedChats.length === 1 ? 'chat' : 'chats'}
            </span>
          </div>
        </div>
        
        {/* Filtros */}
        <div className="flex space-x-2">
          {[
            { key: 'all', label: 'Todos', icon: MessageCircle },
            { key: 'waiting', label: 'Aguardando', icon: Clock },
            { key: 'active', label: 'Ativos', icon: User },
            { key: 'resolved', label: 'Resolvidos', icon: Archive }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`flex items-center space-x-1 px-3 py-1.5 rounded-md text-sm transition-colors ${
                filter === key
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              <Icon className="w-3 h-3" />
              <span>{label}</span>
            </button>
          ))}
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
              <motion.div
                key={chat.chat_id || chat.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
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
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatList


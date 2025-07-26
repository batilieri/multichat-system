import React, { useState, useEffect } from 'react'
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

const ChatList = ({ selectedChat, onSelectChat }) => {
  const [chats, setChats] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, waiting, active, resolved
  const { apiRequest } = useAuth()
  const [isRealtimeConnected, setIsRealtimeConnected] = useState(false)

  // Removido dados mockados - usando apenas dados reais da API

  useEffect(() => {
    loadChats()
  }, [])

  // Função para atualizar chat em tempo real
  const handleChatUpdate = (chatId, chatData) => {
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
  }

  // Usar hook de atualizações em tempo real para lista de chats
  useChatListUpdates(handleChatUpdate)

  const loadChats = async () => {
    try {
      setLoading(true)
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
      // Transformação para garantir campos obrigatórios
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
      }));
      setChats(transformedChats);
      setLoading(false);
    } catch (error) {
      console.error('❌ Erro ao carregar chats:', error)
      setChats([])
      setLoading(false)
      window.alert('Erro ao carregar chats: ' + error.message)
    }
  }

  // Função para buscar a foto de perfil de um contato
  // REMOVIDO: fetchProfilePicture

  // Carregar fotos de perfil após carregar os chats
  useEffect(() => {
    if (!chats.length) return;
    // Não é mais necessário buscar profile_picture individualmente,
    // pois já vem no objeto do chat retornado pela API.
    setChats(chats);
    // eslint-disable-next-line
  }, [loading]);

  const filteredChats = chats.filter(chat => {
    const matchesFilter = filter === 'all' || 
                         (filter === 'waiting' && chat.atribuicao_atual?.status === 'aguardando') ||
                         (filter === 'active' && chat.atribuicao_atual?.status === 'em_andamento') ||
                         (filter === 'resolved' && chat.atribuicao_atual?.status === 'resolvido')
    
    return matchesFilter
  })

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400';
      case 'active':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'closed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  }

  const getPriorityColor = (prioridade) => {
    switch (prioridade) {
      case 'urgente':
        return 'border-l-red-500'
      case 'alta':
        return 'border-l-orange-500'
      case 'normal':
        return 'border-l-blue-500'
      case 'baixa':
        return 'border-l-gray-500'
      default:
        return 'border-l-gray-300'
    }
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return 'agora'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  }

  if (loading) {
    return (
      <div className="h-full bg-background border-r border-border">
        <div className="p-4 space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-center space-x-3 p-3">
                <div className="h-12 w-12 bg-muted rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                  <div className="h-3 bg-muted rounded w-1/2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-background flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-foreground">Chats</h2>
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-accent rounded-lg transition-colors">
              <Filter className="h-4 w-4 text-muted-foreground" />
            </button>
            <button className="p-2 hover:bg-accent rounded-lg transition-colors">
              <MoreVertical className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        </div>



        {/* Filtros */}
        <div className="flex space-x-2">
          {[
            { key: 'all', label: 'Todos' },
            { key: 'waiting', label: 'Aguardando' },
            { key: 'active', label: 'Ativo' },
            { key: 'resolved', label: 'Resolvido' }
          ].map((filterOption) => (
            <button
              key={filterOption.key}
              onClick={() => setFilter(filterOption.key)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                filter === filterOption.key
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-accent'
              }`}
            >
              {filterOption.label}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de chats */}
      <div className="flex-1 overflow-y-auto">
        {filteredChats.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            <div className="text-center">
              <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>Nenhum chat encontrado</p>
            </div>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {filteredChats.map((chat) => (
              <motion.div
                key={chat.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.01 }}
                onClick={() => onSelectChat(chat)}
                className={`
                  p-3 rounded-lg cursor-pointer transition-all duration-200 border-l-4
                  ${selectedChat?.id === chat.id 
                    ? 'bg-accent border-l-primary' 
                    : `bg-card hover:bg-accent ${getPriorityColor(chat.atribuicao_atual?.prioridade)}`
                  }
                `}
              >
                <div className="flex items-start space-x-3">
                  {/* Avatar */}
                  <div className="relative">
                    {(chat.foto_perfil || chat.profile_picture) ? (
                      <img
                        src={chat.foto_perfil || chat.profile_picture}
                        alt={chat.sender_name}
                        className="h-12 w-12 rounded-full object-cover border border-muted"
                        onError={(e) => {
                          // Fallback para ícone se a imagem falhar
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div className={`h-12 w-12 bg-primary rounded-full flex items-center justify-center ${(chat.foto_perfil || chat.profile_picture) ? 'hidden' : ''}`}>
                      {chat.is_group ? (
                        <Users className="h-6 w-6 text-primary-foreground" />
                      ) : (
                        <User className="h-6 w-6 text-primary-foreground" />
                      )}
                    </div>
                    {chat.unread_count > 0 && (
                      <div className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {chat.unread_count}
                      </div>
                    )}
                  </div>

                  {/* Conteúdo */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-medium text-foreground truncate">
                        {chat.is_group ? chat.group_name : chat.contact_name}
                      </h3>
                      <span className="text-xs text-muted-foreground">
                        {formatTime(chat.ultima_mensagem.data)}
                      </span>
                    </div>

                    <p className="text-sm text-muted-foreground truncate mb-2">
                      {chat.ultima_mensagem.conteudo}
                    </p>

                    <div className="flex items-center justify-between">
                      <span className={`
                        px-2 py-1 text-xs rounded-full
                        ${getStatusColor(chat.atribuicao_atual?.status)}
                      `}>
                        {chat.atribuicao_atual?.status === 'aguardando' && 'Aguardando'}
                        {chat.atribuicao_atual?.status === 'em_andamento' && 'Em andamento'}
                        {chat.atribuicao_atual?.status === 'resolvido' && 'Resolvido'}
                      </span>

                      <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                        <MessageCircle className="h-3 w-3" />
                        <span>{chat.total_mensagens}</span>
                      </div>
                    </div>

                    {chat.atribuicao_atual?.usuario && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        Atribuído para: {chat.atribuicao_atual.usuario}
                      </div>
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


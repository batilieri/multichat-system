import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  Check, 
  CheckCheck, 
  Clock, 
  SmilePlus,
  MessageCircle,
  Download,
  Play,
  Pause,
  MoreVertical,
  Info,
  CornerUpLeft,
  Copy,
  Share2,
  Pin,
  Star,
  Trash2,
  Megaphone,
  Pencil,
  Loader2,
  AlertTriangle
} from 'lucide-react'
import EmojiBadge from './EmojiBadge'
import { Popover, PopoverTrigger, PopoverContent } from './ui/popover'
import { Slider } from './ui/slider'
import Emoji from './Emoji'
import EmojiRegex from 'emoji-regex'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from './ui/dropdown-menu'
import { useToast } from "../components/ui/use-toast"
import { togglePinMessage, toggleFavoriteMessage } from '../data/mock/messages'
import { getAllChats } from '../data/mock/chats'

// Tipos de mensagem suportados
const MessageType = {
  TEXT: "texto",
  IMAGE: "imagem",
  VIDEO: "video",
  AUDIO: "audio",
  DOCUMENT: "documento",
  STICKER: "sticker"
};

const Message = ({ message, profilePicture, onReply, hideMenu, onForward, onShowInfo, onDelete }) => {
  // Remover log de debug excessivo
  // console.log('DEBUG MESSAGE OBJETO:', message);
  const [reactions, setReactions] = useState(message.reacoes || message.reactions || [])
  const [isFavorited, setIsFavorited] = useState(message.isFavorited || false)
  const [isPinned, setIsPinned] = useState(message.isPinned || false)
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [showReportModal, setShowReportModal] = useState(false)
  const [isDeleted, setIsDeleted] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editText, setEditText] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [isReactionLoading, setIsReactionLoading] = useState(false)
  const [showReactionPicker, setShowReactionPicker] = useState(false)
  
  // Debug: monitorar mudanças no estado do modal
  useEffect(() => {
    console.log('🔄 Estado do modal alterado:', showEditModal)
  }, [showEditModal])

  // Fechar popover de reações quando clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showReactionPicker) {
        const target = event.target
        if (!target.closest('.reaction-picker')) {
          setShowReactionPicker(false)
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showReactionPicker])
  const { toast } = useToast()

  // Função para lidar com teclas de atalho
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSaveEdit()
    } else if (e.key === 'Escape') {
      e.preventDefault()
      setShowEditModal(false)
    }
  }
  const isMe = message.isOwn || message.from_me || message.fromMe || false
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768
  
  // Debug: verificar se a mensagem é própria
  console.log(`🔍 Debug mensagem ${message.id}:`, {
    isOwn: message.isOwn,
    from_me: message.from_me,
    fromMe: message.fromMe,
    isMe: isMe,
    tipo: message.tipo || message.type,
    content: message.content || message.conteudo,
    canEdit: isMe && (message.tipo === 'text' || message.type === 'text' || message.tipo === 'texto' || message.type === 'texto')
  })

  // Emojis principais para reações (apenas os mais comuns)
  const commonEmojis = ['👍', '❤️', '😂', '😮', '😢', '😡']

  // Função para enviar reação
  const handleReaction = async (emoji) => {
    if (isReactionLoading) return
    
    setIsReactionLoading(true)
    setShowReactionPicker(false)
    
    try {
      const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/reagir/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ emoji })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Atualizar reações localmente
        setReactions(data.reacoes || [])
        
        toast({
          title: "Reação enviada",
          description: data.mensagem || `Reação ${data.acao} com sucesso`,
          duration: 2000,
        })
      } else {
        throw new Error(data.erro || 'Erro ao enviar reação')
      }
    } catch (error) {
      console.error('❌ Erro ao enviar reação:', error)
      toast({
        title: "❌ Erro ao reagir",
        description: error.message || "Não foi possível enviar a reação",
        duration: 4000,
      })
    } finally {
      setIsReactionLoading(false)
    }
  }

  // Função para substituir reação (apenas uma reação por mensagem)
  const handleReplaceReaction = async (emoji) => {
    if (isReactionLoading) return
    
    setIsReactionLoading(true)
    
    try {
      const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/reagir/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ emoji })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Atualizar reações localmente
        setReactions(data.reacoes || [])
        
        toast({
          title: "Reação atualizada",
          description: data.mensagem || `Reação ${data.acao} com sucesso`,
          duration: 2000,
        })
      } else {
        throw new Error(data.erro || 'Erro ao atualizar reação')
      }
    } catch (error) {
      console.error('❌ Erro ao atualizar reação:', error)
      toast({
        title: "❌ Erro ao reagir",
        description: error.message || "Não foi possível atualizar a reação",
        duration: 4000,
      })
    } finally {
      setIsReactionLoading(false)
    }
  }

  // Função para remover reação
  const handleRemoveReaction = async () => {
    if (isReactionLoading) return
    
    setIsReactionLoading(true)
    
    try {
      const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/remover-reacao/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        }
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Atualizar reações localmente
        setReactions(data.reacoes || [])
        
        toast({
          title: "Reação removida",
          description: data.mensagem || "Reação removida com sucesso",
          duration: 2000,
        })
      } else {
        throw new Error(data.erro || 'Erro ao remover reação')
      }
    } catch (error) {
      console.error('❌ Erro ao remover reação:', error)
      toast({
        title: "❌ Erro ao remover reação",
        description: error.message || "Não foi possível remover a reação",
        duration: 4000,
      })
    } finally {
      setIsReactionLoading(false)
    }
  }
  
  // Handlers para cada ação do menu
  const handleReply = () => {
    if (onReply) onReply(message)
  }
  const handleCopy = () => {
    if (message.content || message.conteudo) {
      window.navigator.clipboard.writeText(message.content || message.conteudo)
    }
  }
  const handleDownload = () => {
    if (message.mediaUrl) {
      const link = document.createElement('a')
      link.href = message.mediaUrl
      link.download = message.filename || 'arquivo'
      link.click()
    }
  }
  const handleShare = () => {
    if (navigator.share && message.mediaUrl) {
      navigator.share({ url: message.mediaUrl, title: message.filename || 'Arquivo', text: message.content || message.conteudo || '' })
    }
  }
  const handleFavorite = () => {
    toggleFavoriteMessage(message.id)
    const newFavorited = !isFavorited
    setIsFavorited(newFavorited)
    
    // Feedback visual com toast
    toast({
      title: newFavorited ? "Mensagem favoritada" : "Favorito removido",
      description: newFavorited 
        ? "A mensagem foi adicionada aos seus favoritos" 
        : "A mensagem foi removida dos favoritos",
      duration: 2000,
    })
  }
  const handleForward = () => {
    if (typeof onForward === 'function') onForward(message)
  }
  const handleSelectChat = (chatId) => {
    setSelectedChats(prev => prev.includes(chatId)
      ? prev.filter(id => id !== chatId)
      : [...prev, chatId])
  }
  const handleConfirmForward = () => {
    // Aqui você pode implementar o mock de encaminhamento
    setShowForwardModal(false)
    setSelectedChats([])
    setForwardSearch("")
  }
  const handlePin = () => {
    togglePinMessage(message.id)
    setIsPinned((prev) => !prev)
  }
  const handleInfo = () => {
    if (typeof onShowInfo === 'function') {
      // Mock dos campos de horário para exibição no modal
      const now = new Date()
      const pad = n => n.toString().padStart(2, '0')
      const hora = pad(now.getHours()) + ':' + pad(now.getMinutes())
      onShowInfo({
        ...message,
        entregueEm: message.entregueEm || hora,
        vistaEm: message.vistaEm || (message.status === 'read' ? hora : undefined),
        reproduzidaEm: message.reproduzidaEm || (message.tipo === 'audio' ? hora : undefined)
      })
    }
  }
  const handleReport = () => {
    setShowReportModal(true)
  }
  const handleEdit = async () => {
    console.log('✏️ Editando mensagem ID:', message.id)
    console.log('📋 Dados da mensagem:', {
      id: message.id,
      type: message.type,
      content: message.content,
      conteudo: message.conteudo,
      isOwn: message.isOwn,
      from_me: message.from_me,
      fromMe: message.fromMe
    })
    
    // Verificar se a mensagem pode ser editada (apenas mensagens de texto)
    if (message.type !== 'texto' && message.type !== 'text' && message.tipo !== 'texto' && message.tipo !== 'text') {
      console.log('❌ Tipo de mensagem não permitido:', message.type, message.tipo)
      toast({
        title: "Não é possível editar",
        description: "Apenas mensagens de texto podem ser editadas",
        duration: 3000,
      })
      return
    }
    
    // Verificar se é uma mensagem própria
    if (!isMe) {
      console.log('❌ Mensagem não é própria:', {
        isMe,
        isOwn: message.isOwn,
        from_me: message.from_me,
        fromMe: message.fromMe
      })
      toast({
        title: "Não é possível editar",
        description: "Apenas suas próprias mensagens podem ser editadas",
        duration: 3000,
      })
      return
    }
    
    // Abrir modal de edição
    const textoOriginal = message.content || message.conteudo || ''
    console.log('📝 Texto original:', textoOriginal)
    setEditText(textoOriginal)
    setShowEditModal(true)
    console.log('✅ Modal de edição aberto')
  }

  const handleSaveEdit = async () => {
    const textoLimpo = editText.trim()
    
    // Validações
    if (!textoLimpo) {
      toast({
        title: "Erro",
        description: "O texto não pode estar vazio",
        duration: 3000,
      })
      return
    }

    const textoOriginal = message.content || message.conteudo || ''
    if (textoLimpo === textoOriginal) {
      toast({
        title: "Aviso",
        description: "O texto não foi alterado",
        duration: 2000,
      })
      return
    }

    if (textoLimpo.length > 4096) {
      toast({
        title: "Erro",
        description: "O texto é muito longo (máximo 4096 caracteres)",
        duration: 3000,
      })
      return
    }

    // Verificar se a mensagem tem message_id (necessário para edição)
    if (!message.message_id) {
      toast({
        title: "Erro ao editar",
        description: "Esta mensagem não pode ser editada (sem ID do WhatsApp)",
        duration: 3000,
      })
      return
    }

    setIsEditing(true)
    
    try {
      console.log('🔄 Enviando edição para API...')
      console.log('   - ID da mensagem:', message.id)
      console.log('   - Message ID (WhatsApp):', message.message_id)
      console.log('   - Chat ID:', message.chat?.chat_id)
      console.log('   - Novo texto:', textoLimpo)
      
      // Usar URL relativa (proxy redireciona para backend)
      const apiUrl = `/api/mensagens/${message.id}/editar/`
      console.log('   - URL da API:', apiUrl)
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          novo_texto: textoLimpo
        }),
      })
      
      let data = {}
      try {
        data = await response.json()
      } catch (jsonError) {
        console.warn('Resposta não é JSON válido:', response.status, response.statusText)
        data = { error: `Erro ${response.status}: ${response.statusText}` }
      }
      
      console.log('📡 Resposta da API:', response.status, data)
      
      if (response.ok) {
        // Atualizar a mensagem localmente
        message.content = textoLimpo
        message.conteudo = textoLimpo
        
        setShowEditModal(false)
        setEditText('')
        
        toast({
          title: "✅ Mensagem editada",
          description: data.message || "A mensagem foi editada com sucesso no WhatsApp e no sistema",
          duration: 3000,
        })
        
        console.log('✅ Mensagem editada com sucesso:', data)
        
        // Forçar atualização da interface
        if (message.chat?.chat_id) {
          // Notificar sistema de tempo real sobre a edição
          const updateEvent = new CustomEvent('messageEdited', {
            detail: {
              chat_id: message.chat.chat_id,
              message_id: message.id,
              new_content: textoLimpo
            }
          })
          window.dispatchEvent(updateEvent)
        }
      } else {
        // Tratar diferentes tipos de erro
        let errorMessage = data.error || data.details || `Erro ${response.status}: ${response.statusText}`
        
        if (response.status === 404) {
          errorMessage = "Mensagem não encontrada"
        } else if (response.status === 400) {
          if (data.error?.includes('message_id')) {
            errorMessage = "Esta mensagem não pode ser editada (sem ID do WhatsApp)"
          } else if (data.error?.includes('from_me')) {
            errorMessage = "Apenas mensagens enviadas por você podem ser editadas"
          } else if (data.error?.includes('texto')) {
            errorMessage = "Apenas mensagens de texto podem ser editadas"
          }
        } else if (response.status === 401) {
          errorMessage = "Sessão expirada. Faça login novamente."
        } else if (response.status === 403) {
          errorMessage = "Você não tem permissão para editar esta mensagem"
        }
        
        throw new Error(errorMessage)
      }
    } catch (error) {
      console.error('❌ Erro ao editar mensagem:', error)
      toast({
        title: "❌ Erro ao editar",
        description: error.message || "Não foi possível editar a mensagem",
        duration: 4000,
      })
    } finally {
      setIsEditing(false)
    }
  }
  
  const handleDelete = async () => {
    console.log('🗑️ Excluindo mensagem ID:', message.id, 'message_id:', message.message_id)
    
    // Verificar se a mensagem tem message_id (necessário para exclusão)
    if (!message.message_id) {
      toast({
        title: "Erro ao excluir",
        description: "Esta mensagem não pode ser excluída (sem ID do WhatsApp)",
        duration: 3000,
      })
      return
    }
    
    // Confirmar exclusão
    if (!window.confirm('Tem certeza que deseja excluir esta mensagem?')) {
      return
    }
    
    try {
      // Chamada real à API para excluir mensagem
      const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      })
      
      let data = {}
      try {
        data = await response.json()
      } catch (jsonError) {
        console.warn('Resposta não é JSON válido:', response.status, response.statusText)
        // Se não conseguir fazer parse do JSON, usar status da resposta
        data = { error: `Erro ${response.status}: ${response.statusText}` }
      }
      
      if (response.ok) {
        setIsDeleted(true)
        // Não notificar o componente pai para remover - manter no estado
        toast({
          title: "Mensagem excluída",
          description: "A mensagem foi excluída e marcada como removida",
          duration: 2000,
        })
        console.log('✅ Mensagem excluída com sucesso:', data)
      } else {
        throw new Error(data.error || data.details || `Erro ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Erro ao excluir mensagem:', error)
      toast({
        title: "Erro ao excluir",
        description: error.message || "Não foi possível excluir a mensagem",
        duration: 3000,
      })
    }
  }
  // Não retornar null quando excluída - manter no DOM com visual diferente

  // Função para formatar o horário (mover para o topo do arquivo, se já existir, remova a duplicata)
  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const statusIcon = {
    sent: <Check className="w-4 h-4 text-primary-foreground/70" />,
    received: <CheckCheck className="w-4 h-4 text-primary-foreground/70" />,
    read: <CheckCheck className="w-4 h-4 text-primary-foreground" />,
  }[message.status || "sent"]

  // Aplicando as guidelines de design com melhor contraste
  const hasIconsOrMenu = isPinned || isFavorited || !hideMenu
  
  // Estilo base da bolha
  let bubbleBase = `
    rounded-xl px-4 py-3 text-sm max-w-[75%] shadow-sm
    transition-all duration-200 relative
    ${hasIconsOrMenu ? 'pr-14' : ''}
  `
  
  // Aplicar estilo baseado no estado da mensagem
  if (isDeleted) {
    // Estilo para mensagem excluída - vermelho
    bubbleBase += `
      bg-red-500 text-white rounded-br-none opacity-75
      ${isMe ? 'rounded-br-none' : 'rounded-bl-none'}
    `
  } else {
    // Estilo normal
    bubbleBase += `
      ${isMe
        ? "bg-primary text-primary-foreground rounded-br-none hover:bg-primary/90"
        : "bg-card border border-border text-foreground rounded-bl-none hover:bg-accent"
      }
    `
  }

  // Não precisamos mais do estado hovered, pois os ícones ficam sempre visíveis



  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`w-full ${isMe ? 'flex justify-end' : 'flex justify-start'}`}
    >
      {/* Avatar do contato para mensagens recebidas */}
      {!isMe && profilePicture && (
        <img
          src={profilePicture}
          alt="Foto do contato"
          className="h-8 w-8 rounded-full mr-2 object-cover border border-muted"
          onError={e => { e.target.style.display = 'none'; }}
        />
      )}
      <motion.div
        className={bubbleBase.replace(/pr-\d+|pr-\[.*?\]|pr-0/g, '') + ' w-fit relative'}
        whileHover={{ scale: 1.01 }}
        transition={{ duration: 0.2 }}
      >
        {/* Nome do remetente em grupos (apenas para mensagens de outros) */}
        {!isMe && message.sender_display_name && (
          <div className="text-xs font-medium text-muted-foreground mb-1 px-1">
            {message.sender_display_name}
          </div>
        )}
        
        {/* Conteúdo da mensagem sempre em cima */}
        <div className="mb-1">
          {/* Header da mensagem - Encaminhada */}
          {message.isForwarded && (
            <div className="text-xs text-muted-foreground/80 mb-1 px-1 font-medium border-b border-muted-foreground/20 pb-1">
              ↳ Encaminhada
            </div>
          )}
          {/* Reply inline dentro da bolha */}
          {message.replyTo && (
            <motion.div 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={
                `mb-2 pl-2 border-l-2 text-xs rounded-r-md px-2 py-1 ` +
                (isMe
                  ? 'bg-card text-foreground border-primary/60'
                  : 'bg-primary text-primary-foreground border-primary')
              }
            >
              <span className={isMe ? 'font-semibold block text-primary' : 'font-semibold block text-primary-foreground'}>
                {message.replyTo.type === 'sent' ? "Você" : "Contato"}
              </span>
              <span className="truncate block">
                {message.replyTo.content || "Mídia"}
              </span>
            </motion.div>
          )}
          {/* Conteúdo principal */}
          <div className="message-content">
            {/* Mostrar texto original da mensagem */}
            {(message.tipo === 'texto' || message.type === 'text' || message.type === 'texto')
              ? renderTextWithEmojis(message.content || message.conteudo)
              : message.content}
            
            {/* Indicador de exclusão se a mensagem foi excluída */}
            {isDeleted && (
              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/20">
                <Trash2 className="w-4 h-4" />
                <span className="italic text-sm opacity-90">Esta mensagem foi excluída</span>
              </div>
            )}
          </div>
        </div>
        {/* Linha compacta de ações/reações/status */}
        <div className="flex flex-row justify-between items-center pt-1 min-h-[28px] text-xs w-full">
          {/* Reações (se houver) - à esquerda */}
          <div className="flex flex-wrap items-center gap-2">
            {reactions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-wrap gap-1 flex-none"
                style={{ maxWidth: '120px' }}
              >
                {reactions.slice(0, 6).map((reaction, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleRemoveReaction()}
                    className="w-6 h-6 flex items-center justify-center rounded-full bg-primary-foreground/20 border border-border text-primary-foreground cursor-pointer transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
                    title={`Remover reação ${reaction}`}
                    disabled={isReactionLoading}
                  >
                    <span className="text-xs">{reaction}</span>
                  </motion.button>
                ))}
              </motion.div>
            )}
          </div>
          
          {/* Ações à direita */}
          <div className="flex items-center gap-1">
            {/* Botão de reação simples */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowReactionPicker(!showReactionPicker)}
              className="p-1.5 rounded-full hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring relative reaction-picker"
              title="Adicionar reação"
              disabled={isReactionLoading}
            >
              <SmilePlus className="w-4 h-4 text-muted-foreground" />
              
              {/* Popover de emojis principais */}
              {showReactionPicker && (
                <div className={`absolute bottom-full mb-1 bg-background border border-border rounded-lg shadow-lg p-2 z-50 reaction-picker min-w-[120px] ${
                  isMe ? 'left-0' : 'right-0'
                }`}>
                  <div className="grid grid-cols-3 gap-1">
                    {commonEmojis.map((emoji, index) => (
                      <motion.button
                        key={index}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => handleReaction(emoji)}
                        className="p-1 rounded-full hover:bg-accent transition-colors text-lg flex items-center justify-center"
                        title={`Reagir com ${emoji}`}
                        disabled={isReactionLoading}
                      >
                        {emoji}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}
            </motion.button>
            
            {/* Menu de ações */}
            {!hideMenu && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-1.5 rounded-full hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring">
                    <MoreVertical className="w-4 h-4 text-muted-foreground" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align={isMe ? 'end' : 'start'} className="min-w-[180px]">
                  {/* Responder - sempre */}
                  <DropdownMenuItem onClick={handleReply}>
                    <CornerUpLeft className="w-4 h-4 mr-2" /> Responder
                  </DropdownMenuItem>
                  {/* Copiar - só para texto */}
                  {((message.tipo || message.type) === MessageType.TEXT || (message.tipo || message.type) === 'texto' || (message.tipo || message.type) === 'text') && (
                    <DropdownMenuItem onClick={handleCopy}>
                      <Copy className="w-4 h-4 mr-2" /> Copiar
                    </DropdownMenuItem>
                  )}
                  {/* Baixar e Compartilhar - só para mídia, documento, áudio */}
                  {(message.tipo === MessageType.IMAGE || message.tipo === MessageType.VIDEO || message.tipo === MessageType.DOCUMENT || message.tipo === MessageType.AUDIO) && (
                    <>
                      <DropdownMenuItem onClick={handleDownload}>
                        <Download className="w-4 h-4 mr-2" /> Baixar
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={handleShare}>
                        <Share2 className="w-4 h-4 mr-2" /> Compartilhar
                      </DropdownMenuItem>
                    </>
                  )}
                  {/* Favoritar - sempre */}
                  <DropdownMenuItem onClick={handleFavorite}>
                    <Star className={`w-4 h-4 mr-2 ${isFavorited ? 'text-yellow-500' : ''}`} /> Favoritar
                  </DropdownMenuItem>
                  {/* Encaminhar - sempre */}
                  <DropdownMenuItem onClick={handleForward}>
                    <Share2 className="w-4 h-4 mr-2" /> Encaminhar
                  </DropdownMenuItem>
                  {/* Fixar - sempre (opcional, normalmente só em grupos) */}
                  <DropdownMenuItem onClick={handlePin}>
                    <Pin className={`w-4 h-4 mr-2 ${isPinned ? 'text-primary' : ''}`} /> Fixar
                  </DropdownMenuItem>
                  {/* Info - só para mensagens do usuário */}
                  {isMe && (
                    <DropdownMenuItem onClick={handleInfo}>
                      <Info className="w-4 h-4 mr-2" /> Dados da mensagem
                    </DropdownMenuItem>
                  )}
                  {/* Denunciar - só para mensagens de outros */}
                  {!isMe && (
                    <DropdownMenuItem onClick={handleReport}>
                      <Megaphone className="w-4 h-4 mr-2" /> Denunciar
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  {/* Editar - só para mensagens do usuário */}
                  {(() => {
                    const canEdit = isMe && (message.tipo === 'text' || message.type === 'text' || message.tipo === 'texto' || message.type === 'texto')
                    console.log(`🔍 Renderizando opção editar para mensagem ${message.id}:`, {
                      isMe,
                      messageTipo: message.tipo,
                      messageType: message.type,
                      canEdit
                    })
                    return canEdit ? (
                      <DropdownMenuItem onClick={handleEdit}>
                        <Pencil className="w-4 h-4 mr-2" /> Editar
                      </DropdownMenuItem>
                    ) : null
                  })()}
                  {/* Apagar - sempre, destructive */}
                  <DropdownMenuItem variant="destructive" onClick={handleDelete}>
                    <Trash2 className="w-4 h-4 mr-2" /> Apagar
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
            {/* Horário da mensagem e status de entrega */}
            {isMe && (
              <motion.span 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="ml-1"
              >
                {statusIcon}
              </motion.span>
            )}
            <span className="ml-2 text-muted-foreground select-none">
              {formatTime(message.timestamp)}
            </span>
          </div>
        </div>
      </motion.div>
      
      {/* Modais para Forward, Info, Report */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-xl min-w-[300px]">
            <h2 className="font-bold text-lg mb-2">Denunciar mensagem</h2>
            <div className="text-sm mb-4">Funcionalidade de denúncia mockada.</div>
            <button className="px-4 py-2 rounded bg-primary text-primary-foreground" onClick={() => setShowReportModal(false)}>Fechar</button>
          </div>
        </div>
      )}
      
      {/* Modal de edição */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4 shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Editar mensagem</h2>
              <button 
                onClick={() => setShowEditModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                disabled={isEditing}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Texto original:
              </label>
              <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded text-sm text-gray-600 dark:text-gray-300 mb-4 border">
                {message.content || message.conteudo || 'Sem conteúdo'}
              </div>
              
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Novo texto:
              </label>
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                rows={4}
                placeholder="Digite o novo texto..."
                autoFocus
                disabled={isEditing}
              />
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {editText.length}/4096 caracteres
              </div>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowEditModal(false)}
                disabled={isEditing}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={!editText.trim() || isEditing}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                {isEditing ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Editando...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Salvar
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

// Componente de áudio customizado
const AudioPlayer = ({ message }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [audioUrl, setAudioUrl] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)
    const handleLoadedData = () => {
      setIsLoading(false)
      setDuration(audio.duration)
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('loadeddata', handleLoadedData)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('loadeddata', handleLoadedData)
    }
  }, [])

  // Determinar URL do áudio
  useEffect(() => {
    console.log('🎵 DEBUG AudioPlayer - Dados da mensagem:', message);
    let url = null
    
    // Prioridade 1: URL da pasta /wapi/midias/ (sistema integrado)
    if (message.content || message.conteudo) {
      try {
        const content = message.content || message.conteudo
        let jsonContent
        
        if (typeof content === 'string') {
          jsonContent = JSON.parse(content)
        } else {
          jsonContent = content
        }
        
        if (jsonContent.audioMessage) {
          const audioMessage = jsonContent.audioMessage
          
          // Prioridade 1a: URL da pasta /wapi/midias/audios/
          if (audioMessage.url && audioMessage.url.startsWith('/wapi/midias/')) {
            const filename = audioMessage.url.split('/').pop()
            url = `http://localhost:8000/api/wapi-media/audios/${filename}`
            console.log('🎵 URL /wapi/midias/:', url);
          }
          // Prioridade 1b: Nome do arquivo na pasta /wapi/midias/
          else if (audioMessage.fileName) {
            url = `http://localhost:8000/api/wapi-media/audios/${audioMessage.fileName}`
            console.log('🎵 URL por fileName:', url);
          }
          // Prioridade 1c: URL direta do JSON
          else if (audioMessage.url) {
            url = audioMessage.url
            console.log('🎵 URL direta do JSON:', url);
          }
        }
      } catch (e) {
        console.warn('🎵 Não foi possível extrair URL do áudio:', e)
      }
    }
    
    // Prioridade 2: URL processada do backend (/media/)
    if (!url && message.mediaUrl && message.mediaUrl.startsWith('/media/')) {
      url = `http://localhost:8000${message.mediaUrl}`
      console.log('🎵 URL processada do backend:', url);
    }
    
    // Prioridade 3: URL processada como caminho relativo
    if (!url && message.mediaUrl && message.mediaUrl.startsWith('audios/')) {
      url = `http://localhost:8000/media/${message.mediaUrl}`
      console.log('🎵 URL relativa:', url);
    }
    
    // Prioridade 4: URL direta do WhatsApp (ainda criptografada)
    if (!url && message.mediaUrl && message.mediaUrl.startsWith('http')) {
      url = message.mediaUrl
      console.log('🎵 URL direta do WhatsApp:', url);
    }
    
    // Fallback: usar endpoint da API para servir áudio pelo ID da mensagem
    if (!url && message.id) {
      url = `http://localhost:8000/api/audio/message/${message.id}/`
      console.log('🎵 URL fallback por ID:', url);
    }
    
    console.log('🎵 URL final do áudio:', url);
    setAudioUrl(url)
  }, [message])

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
    }
  }

  const handleSliderChange = (value) => {
    if (audioRef.current && duration > 0) {
      const newTime = (value[0] / 100) * duration
      audioRef.current.currentTime = newTime
      setCurrentTime(newTime)
    }
  }

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const sliderValue = duration > 0 ? [(currentTime / duration) * 100] : [0]

  // Se não há URL de áudio, mostrar mensagem de erro
  if (!audioUrl) {
    return (
      <div className="space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent border border-border rounded-lg p-4"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500 rounded-lg text-white">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-foreground">Áudio não disponível</p>
              <p className="text-xs text-muted-foreground">
                Este áudio não pode ser reproduzido
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {/* Comentário do áudio */}
      {message.content && message.tipo !== 'texto' && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm opacity-90 mb-2"
        >
          {message.content}
        </motion.p>
      )}
      {/* Áudio no estilo do documento */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-accent border border-border rounded-lg p-4 hover:bg-accent/80 transition-colors"
      >
        <div className="flex items-center gap-3">
          {/* Ícone Play/Loading */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={togglePlay}
            disabled={isLoading}
            className={`p-2 rounded-lg shadow-sm transition-colors ${
              isLoading 
                ? 'bg-muted text-muted-foreground cursor-not-allowed' 
                : 'bg-primary text-primary-foreground hover:bg-primary/90'
            }`}
            title={isLoading ? 'Carregando...' : (isPlaying ? 'Pausar' : 'Reproduzir')}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5" />
            )}
          </motion.button>
          
          {/* Informações do áudio */}
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">
              {message.filename || 'Áudio'}
            </p>
            <p className="text-xs text-muted-foreground">
              {isLoading ? 'Carregando...' : (message.duration || formatTime(duration))}
            </p>
            
            {/* Slider de progresso */}
            {!isLoading && (
              <div className="mt-2">
                <Slider
                  value={sliderValue}
                  onValueChange={handleSliderChange}
                  max={100}
                  step={0.1}
                  className="w-full"
                  disabled={isLoading}
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Botão de download */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 hover:bg-background rounded-lg transition-colors"
            title="Baixar áudio"
            onClick={() => {
              if (audioUrl) {
                const link = document.createElement('a')
                link.href = audioUrl
                link.download = `audio_${message.id || Date.now()}.mp3`
                link.click()
              }
            }}
          >
            <Download className="w-4 h-4 text-foreground/80" />
          </motion.button>
        </div>
        
        {/* Player de áudio oculto para funcionalidade */}
        <audio 
          ref={audioRef}
          className="hidden"
          preload="metadata"
          src={audioUrl}
          onError={(e) => {
            console.error('Erro ao carregar áudio:', e)
            setIsLoading(false)
          }}
        />
      </motion.div>
    </div>
  )
}

// Função utilitária para renderizar texto com emojis usando o componente Emoji
function renderTextWithEmojis(text) {
  // Simplificar para evitar problemas com emojis
  if (!text) return '';
  text = typeof text === 'string' ? text : String(text);
  
  // Se o texto contém apenas caracteres simples, retornar diretamente
  if (/^[a-zA-Z0-9\s.,!?;:()\-_@#$%&*+=<>[\]{}|\\/"'`~]+$/.test(text)) {
    return text;
  }
  
  // Para textos com emojis, usar regex mais simples
  try {
    const regex = EmojiRegex();
    const parts = [];
    let lastIndex = 0;
    
    for (const match of text.matchAll(regex)) {
      const emoji = match[0];
      const index = match.index;
      if (index > lastIndex) {
        parts.push(text.slice(lastIndex, index));
      }
      parts.push(<Emoji key={index}>{emoji}</Emoji>);
      lastIndex = index + emoji.length;
    }
    
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    
    return parts;
  } catch (error) {
    console.warn('Erro ao processar emojis:', error);
    return text; // Fallback para texto simples
  }
}

function renderMessageContent(message) {
  // Debug: verificar dados da mensagem
  console.log('🎵 DEBUG renderMessageContent:', {
    id: message.id,
    tipo: message.tipo,
    type: message.type,
    content: message.content,
    conteudo: message.conteudo,
    mediaUrl: message.mediaUrl,
    mediaType: message.mediaType
  });

  // Suporte tanto para 'texto' (pt) quanto 'text' (en)
  const tipo = message.tipo || message.type;
  const showContent = tipo !== 'texto' && tipo !== 'text' && message.content;

  // Debug: verificar tipo
  console.log('🎯 Tipo detectado:', tipo);
  console.log('🎯 MessageType.AUDIO:', MessageType.AUDIO);
  console.log('🎯 É áudio?', tipo === MessageType.AUDIO);

  if (tipo === MessageType.TEXT || tipo === 'texto' || tipo === 'text') {
    return (
      <motion.p 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="whitespace-pre-wrap leading-relaxed pr-8"
      >
          {renderTextWithEmojis(message.conteudo)}
      </motion.p>
    )
  }

  switch (tipo) {
    case MessageType.IMAGE:
      return (
        <div className="space-y-2">
          {/* Comentário da imagem */}
          {showContent && (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm opacity-90 mb-2"
            >
              {message.content}
            </motion.p>
          )}
          
          {/* Imagem */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative group"
          >
            <img
              src={message.mediaUrl || ""}
              alt="Imagem"
              className="rounded-lg max-h-[300px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
            />
            <motion.button
              initial={{ opacity: 0 }}
              whileHover={{ opacity: 1 }}
              className="absolute top-2 right-2 p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
            >
              <Download className="w-4 h-4" />
            </motion.button>
          </motion.div>
        </div>
      )

    case MessageType.VIDEO:
      return (
        <div className="space-y-2">
          {/* Comentário do vídeo */}
          {showContent && (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm opacity-90 mb-2"
            >
              {message.content}
            </motion.p>
          )}
          
          {/* Vídeo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative group"
          >
            <video 
              controls 
              className="rounded-lg max-h-[300px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <source src={message.mediaUrl} type="video/mp4" />
            </video>
            <motion.button
              initial={{ opacity: 0 }}
              whileHover={{ opacity: 1 }}
              className="absolute top-2 right-2 p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
            >
              <Download className="w-4 h-4" />
            </motion.button>
          </motion.div>
        </div>
      )

    case MessageType.AUDIO:
      console.log('🎵 Renderizando AudioPlayer para mensagem:', message.id);
      return <AudioPlayer message={message} />

    case MessageType.DOCUMENT:
      return (
        <div className="space-y-2">
          {/* Comentário do documento */}
          {showContent && (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm opacity-90 mb-2"
            >
              {message.content}
            </motion.p>
          )}
          
          {/* Documento */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-accent border border-border rounded-lg p-4 hover:bg-accent/80 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-lg">
                <MessageCircle className="w-5 h-5 text-primary-foreground" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-foreground">
                  {message.documentFilename || 'Documento'}
                </p>
                <p className="text-xs text-muted-foreground">
                  {message.documentMimetype || 'Tipo desconhecido'}
                </p>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 hover:bg-background rounded-lg transition-colors"
                title="Baixar documento"
                onClick={() => {
                  if (message.documentUrl) {
                    const link = document.createElement('a')
                    link.href = message.documentUrl
                    link.download = message.documentFilename || 'documento'
                    link.click()
                  }
                }}
              >
                <Download className="w-4 h-4 text-foreground/80" />
              </motion.button>
            </div>
          </motion.div>
        </div>
      )

    case MessageType.STICKER:
      return (
        <div className="space-y-2">
          {/* Sticker */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative group"
          >
            <img
              src={message.mediaUrl || ""}
              alt="Sticker"
              className="rounded-lg max-h-[200px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
            />
            <motion.button
              initial={{ opacity: 0 }}
              whileHover={{ opacity: 1 }}
              className="absolute top-2 right-2 p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
            >
              <Download className="w-4 h-4" />
            </motion.button>
          </motion.div>
        </div>
      )

    default:
      // Fallback para mensagens não reconhecidas
      console.log('⚠️ Tipo de mensagem não reconhecido:', tipo);
      return (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="whitespace-pre-wrap leading-relaxed pr-8"
        >
          {renderTextWithEmojis(message.conteudo || message.content || '[Mensagem não suportada]')}
        </motion.p>
      )
  }
}

export { MessageType };
export default Message; 
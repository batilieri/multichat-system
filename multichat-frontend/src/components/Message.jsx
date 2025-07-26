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
  Smile,
  Share2,
  Pin,
  Star,
  Trash2,
  Megaphone,
  Pencil
} from 'lucide-react'
import EmojiBadge from './EmojiBadge'
import { Popover, PopoverTrigger, PopoverContent } from './ui/popover'
import { Slider } from './ui/slider'
import { EmojiReactionBar } from './EmojiReactionBar'
import Emoji from './Emoji'
import EmojiRegex from 'emoji-regex'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from './ui/dropdown-menu'
import { useToast } from "../components/ui/use-toast"
import { togglePinMessage, toggleFavoriteMessage } from '../data/mock/messages'
import EmojiPicker from './EmojiPicker'
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

const Message = ({ message, profilePicture, onReply, hideMenu, onForward, onShowInfo }) => {
  // Remover log de debug excessivo
  // console.log('DEBUG MESSAGE OBJETO:', message);
  const [showReactionButton, setShowReactionButton] = useState(false)
  const [showReactionPopover, setShowReactionPopover] = useState(false)
  const [showFullPicker, setShowFullPicker] = useState(false)
  const [reactions, setReactions] = useState(message.reactions || [])
  const [isFavorited, setIsFavorited] = useState(message.isFavorited || false)
  const [isPinned, setIsPinned] = useState(message.isPinned || false)
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [showReportModal, setShowReportModal] = useState(false)
  const [isDeleted, setIsDeleted] = useState(false)
  const { toast } = useToast()
  const isMe = message.isOwn
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768
  const [popoverSide, setPopoverSide] = useState('top')
  const [popoverAlign, setPopoverAlign] = useState('start')
  const reactionButtonRef = useRef(null)
  const [anchorRect, setAnchorRect] = useState(null)

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
  const handleReact = () => {
    if (reactionButtonRef.current) {
      const rect = reactionButtonRef.current.getBoundingClientRect()
      setPopoverSide(rect.top < 250 ? 'bottom' : 'top')
    }
    setShowReactionPopover(true)
    setShowFullPicker(true)
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
    
    // Verificar se a mensagem pode ser editada (apenas mensagens de texto)
    if (message.type !== 'texto' && message.type !== 'text') {
      toast({
        title: "Não é possível editar",
        description: "Apenas mensagens de texto podem ser editadas",
        duration: 3000,
      })
      return
    }
    
    // TODO: Implementar modal de edição
    // Por enquanto, apenas mostrar o ID
    toast({
      title: "Editar mensagem",
      description: `Editando mensagem ID: ${message.id}`,
      duration: 2000,
    })
  }
  
  const handleDelete = async () => {
    console.log('🗑️ Excluindo mensagem ID:', message.id)
    
    // Confirmar exclusão
    if (!window.confirm('Tem certeza que deseja excluir esta mensagem?')) {
      return
    }
    
    try {
      // Chamada real à API para excluir mensagem
      const response = await fetch(`/api/mensagens/${message.id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setIsDeleted(true)
        toast({
          title: "Mensagem excluída",
          description: data.message || "A mensagem foi excluída com sucesso",
          duration: 2000,
        })
        console.log('✅ Mensagem excluída com sucesso:', data)
      } else {
        throw new Error(data.error || data.details || 'Erro ao excluir mensagem')
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
  if (isDeleted) return null

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
  const bubbleBase = `
    rounded-xl px-4 py-3 text-sm max-w-[75%] shadow-sm
    transition-all duration-200 relative
    ${hasIconsOrMenu ? 'pr-14' : ''}
    ${isMe
      ? "bg-primary text-primary-foreground rounded-br-none hover:bg-primary/90"
      : "bg-card border border-border text-foreground rounded-bl-none hover:bg-accent"
    }
  `

  // Não precisamos mais do estado hovered, pois os ícones ficam sempre visíveis

  function handleAddReaction(emoji) {
    if (reactions.includes(emoji)) {
      setReactions((prev) => prev.filter((r) => r !== emoji))
    } else {
      setReactions((prev) => [...prev, emoji])
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`w-full ${isMe ? 'flex justify-end' : 'flex justify-start'}`}
      // Removido onMouseEnter/onMouseLeave/onFocus/onBlur
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
            {/* Renderizar texto com emojis se for mensagem de texto */}
            {(message.tipo === 'texto' || message.type === 'text' || message.type === 'texto')
              ? renderTextWithEmojis(message.content || message.conteudo)
              : message.content}
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
                className="grid grid-cols-3 gap-1 flex-none"
                style={{ maxWidth: '120px' }}
              >
                {reactions.map((r, i) => (
                  <EmojiBadge
                    key={i}
                    onClick={() => handleAddReaction(r)}
                    title="Remover reação"
                    label={"Remover reação " + r}
                  >
                    {r}
                  </EmojiBadge>
                ))}
              </motion.div>
            )}
          </div>
          {/* Ícones e ações - à direita */}
          <div className="flex flex-row items-center gap-2 ml-auto">
            {/* Ícones de pin e favorito juntos, antes do emoji */}
            {isPinned && (
              <Pin
                className={`w-4 h-4 ${isMe ? 'text-primary-foreground' : 'text-primary'}`}
                title="Mensagem fixada"
              />
            )}
            {isFavorited && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="flex items-center justify-center"
              >
                <Star className="w-4 h-4 text-yellow-500" title="Favorita" />
              </motion.div>
            )}
            {/* Botão de reações */}
            <Popover open={showReactionPopover} onOpenChange={open => {
              setShowReactionPopover(open)
              if (!open) setShowFullPicker(false)
            }}>
              <motion.button
                ref={reactionButtonRef}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={e => {
                  e.stopPropagation();
                  if (reactionButtonRef.current) {
                    const rect = reactionButtonRef.current.getBoundingClientRect();
                    setAnchorRect(rect);
                    // Detecta se está próximo da borda inferior
                    const isBottom = rect.bottom + 220 > window.innerHeight; // 220px altura estimada do popover
                    // Detecta se está próximo da borda direita
                    const isRight = rect.right + 320 > window.innerWidth; // 320px largura estimada do popover
                    setPopoverSide(isBottom ? 'top' : 'bottom');
                    setPopoverAlign(isRight ? 'end' : 'start');
                  }
                  setShowReactionPopover(true)
                }}
                className="p-1 bg-background border border-border rounded-full shadow-sm hover:bg-accent transition-all duration-200 flex items-center justify-center w-7 h-7 min-w-0 min-h-0"
                title="Reagir"
                style={{ lineHeight: 1 }}
              >
                <SmilePlus className="w-4 h-4 text-muted-foreground" />
              </motion.button>
              {showReactionPopover && (
                <PopoverContent
                  anchorRect={anchorRect}
                  onClose={() => setShowReactionPopover(false)}
                  side={popoverSide}
                  align={popoverAlign}
                  sideOffset={16}
                  className="bg-popover border border-border p-3 rounded-xl shadow-lg max-h-[60vh] overflow-y-auto"
                >
                  {!showFullPicker ? (
                    <EmojiReactionBar
                      onSelect={handleAddReaction}
                      onOpenFullPicker={() => setShowFullPicker(true)}
                      isReversed={isMe}
                    />
                  ) : (
                    <EmojiPicker
                      onSelect={emoji => { handleAddReaction(emoji); setShowReactionPopover(false); setShowFullPicker(false) }}
                      onClose={() => { setShowFullPicker(false) }}
                    />
                  )}
                </PopoverContent>
              )}
            </Popover>
            {/* Menu de opções */}
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
                  {/* Reagir - sempre */}
                  <DropdownMenuItem onClick={handleReact}>
                    <Smile className="w-4 h-4 mr-2" /> Reagir
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
                  {isMe && (
                    <DropdownMenuItem onClick={handleEdit}>
                      <Pencil className="w-4 h-4 mr-2" /> Editar
                    </DropdownMenuItem>
                  )}
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
      </motion.div>
    </motion.div>
  )
}

// Componente de áudio customizado
const AudioPlayer = ({ message }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [])

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
          {/* Ícone Play */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={togglePlay}
            className="p-2 bg-primary rounded-lg text-primary-foreground shadow-sm hover:bg-primary/90 transition-colors"
            title={isPlaying ? 'Pausar' : 'Reproduzir'}
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </motion.button>
          {/* Informações do áudio */}
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">
              {message.filename || 'Áudio'}
            </p>
            <p className="text-xs text-muted-foreground">
              {message.duration || formatTime(duration)}
            </p>
            {/* Slider de progresso */}
            <div className="mt-2">
              <Slider
                value={sliderValue}
                onValueChange={handleSliderChange}
                max={100}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
          </div>
          {/* Botão de download */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 hover:bg-background rounded-lg transition-colors"
            title="Baixar áudio"
          >
            <Download className="w-4 h-4 text-foreground/80" />
          </motion.button>
        </div>
        {/* Player de áudio oculto para funcionalidade */}
        <audio 
          ref={audioRef}
          className="hidden"
          preload="metadata"
        >
          <source src={message.mediaUrl} type="audio/mpeg" />
          <source src={message.mediaUrl} type="audio/mp4" />
          <source src={message.mediaUrl} type="audio/wav" />
        </audio>
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
  // Suporte tanto para 'texto' (pt) quanto 'text' (en)
  const tipo = message.tipo || message.type;
  const showContent = tipo !== 'texto' && tipo !== 'text' && message.content;

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
                  {message.filename || "Documento"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {message.filesize || "Tamanho desconhecido"}
                </p>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 hover:bg-background rounded-lg transition-colors"
              >
                <Download className="w-4 h-4 text-muted-foreground" />
              </motion.button>
            </div>
          </motion.div>
        </div>
      )

    case MessageType.STICKER:
      return (
        <div className="space-y-2">
          {/* Comentário do sticker */}
          {showContent && (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm opacity-90 mb-2"
            >
              {message.content}
            </motion.p>
          )}
          
          {/* Sticker */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-block"
          >
            <img
              src={message.mediaUrl || ""}
              alt="Sticker"
              className="rounded-lg w-32 h-32 object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
            />
          </motion.div>
        </div>
      )

    default:
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-muted-foreground italic"
        >
          Mensagem não suportada
        </motion.div>
      )
  }
}

export { MessageType };
export default Message; 
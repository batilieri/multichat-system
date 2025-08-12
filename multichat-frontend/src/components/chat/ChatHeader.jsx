import React from 'react'
import {
  Phone,
  Video,
  Heart,
  Pin,
  MoreVertical
} from 'lucide-react'
import { motion } from 'framer-motion'

const ChatHeader = ({ 
  chat, 
  isConnected, 
  favoritedMessages, 
  pinnedMessages, 
  onOpenContactInfo, 
  onOpenImageModal, 
  onOpenFavoritesModal, 
  onOpenPinsModal 
}) => {
  return (
    <div className="flex items-center gap-4 p-4 border-b border-border bg-card sticky top-0 z-10">
      {/* Área clicável para abrir o perfil (exceto imagem) */}
      <div className="flex items-center gap-4 flex-1 cursor-pointer select-none" onClick={onOpenContactInfo}>
        <div 
          className="h-10 w-10 bg-primary rounded-full flex items-center justify-center overflow-hidden cursor-pointer" 
          onClick={e => { 
            e.stopPropagation(); 
            if (chat.foto_perfil || chat.profile_picture) onOpenImageModal(); 
          }}
        >
          {chat.foto_perfil || chat.profile_picture ? (
            <img
              src={chat.foto_perfil || chat.profile_picture}
              alt={chat.contact_name || chat.sender_name || chat.chat_id}
              className="h-full w-full object-cover"
              onError={e => {
                e.target.style.display = 'none';
                e.target.nextSibling && (e.target.nextSibling.style.display = 'flex');
              }}
            />
          ) : (
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="h-5 w-5 text-primary-foreground">
              <circle cx="12" cy="7" r="4" />
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
            </svg>
          )}
        </div>
        <div className="flex flex-col min-w-0">
          <span className="font-semibold truncate text-foreground text-base">
            {chat.contact_name || chat.sender_name || chat.group_name || chat.chat_id}
          </span>
          <span className="text-xs text-muted-foreground truncate">
            {chat.status || chat.phone || chat.chat_id}
          </span>
        </div>
      </div>

      {/* Indicador de status de tempo real */}
      <div className="flex items-center space-x-1 mr-2">
        {isConnected ? (
          <>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-600 font-medium">Tempo real</span>
          </>
        ) : (
          <>
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="text-xs text-red-600 font-medium">Offline</span>
          </>
        )}
      </div>

      {/* Botões de ação do header */}
      <div className="flex items-center space-x-2">
        <button className="p-2 hover:bg-accent rounded-lg transition-colors">
          <Phone className="h-4 w-4 text-muted-foreground" />
        </button>
        <button className="p-2 hover:bg-accent rounded-lg transition-colors">
          <Video className="h-4 w-4 text-muted-foreground" />
        </button>
        
        {/* Botão de favoritas */}
        <button
          className="p-2 hover:bg-yellow-500/20 rounded-lg transition-colors relative"
          onClick={onOpenFavoritesModal}
          title="Mensagens favoritas"
        >
          <Heart className="h-4 w-4 text-yellow-500" />
          {favoritedMessages.length > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 bg-yellow-500 text-white rounded-full text-xs px-1.5 py-0.5 font-medium"
            >
              {favoritedMessages.length}
            </motion.span>
          )}
        </button>
        
        {/* Botão de pins */}
        <button 
          className="p-2 hover:bg-primary/20 rounded-lg transition-colors relative" 
          onClick={onOpenPinsModal} 
          title="Mensagens fixadas"
        >
          <Pin className="h-4 w-4 text-primary" />
          {pinnedMessages.length > 0 && (
            <span className="absolute -top-1 -right-1 bg-primary text-primary-foreground rounded-full text-xs px-1.5 py-0.5">
              {pinnedMessages.length}
            </span>
          )}
        </button>
        
        <button className="p-2 hover:bg-accent rounded-lg transition-colors">
          <MoreVertical className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>
    </div>
  )
}

export default ChatHeader;

import React from 'react'
import { motion } from 'framer-motion'
import {
  Send,
  Paperclip,
  Smile,
  X
} from 'lucide-react'
import EmojiPicker from '../EmojiPicker'
import { Button } from '../ui/button'

const MessageInput = ({
  message,
  setMessage,
  replyTo,
  setReplyTo,
  pendingImage,
  setPendingImage,
  imageCaption,
  setImageCaption,
  isProcessingImage,
  showEmojiPicker,
  setShowEmojiPicker,
  showImageUpload,
  setShowImageUpload,
  onSendMessage,
  onSendPendingImage,
  onEmojiSelect
}) => {
  return (
    <div className="p-4 border-t border-border bg-card">
      {/* Se estiver respondendo, mostrar a mensagem acima do input */}
      {replyTo && (
        <div className="mb-2 p-2 bg-accent/50 border-l-4 border-primary rounded flex items-center justify-between">
          <div>
            <span className="font-semibold text-primary mr-2">Respondendo:</span>
            <span className="text-sm text-muted-foreground">{replyTo.conteudo || 'Mídia'}</span>
          </div>
          <button onClick={() => setReplyTo(null)} className="ml-2 p-1 rounded hover:bg-accent transition-colors">
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>
      )}

      {/* Área de imagem pendente */}
      {pendingImage && (
        <div className="mb-3 p-3 bg-accent/30 border border-border rounded-lg">
          <div className="flex items-start gap-3">
            <img
              src={`data:image/png;base64,${pendingImage.data}`}
              alt="Imagem para enviar"
              className="w-16 h-16 object-cover rounded-lg"
            />
            <div className="flex-1">
              <div className="text-sm text-muted-foreground mb-2">Imagem pronta para enviar</div>
              <input
                type="text"
                value={imageCaption}
                onChange={(e) => setImageCaption(e.target.value)}
                placeholder="Legenda (opcional)"
                className="w-full px-3 py-2 text-sm border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <button
              onClick={() => setPendingImage(null)}
              className="p-1 rounded-full hover:bg-accent transition-colors"
              title="Cancelar"
            >
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </div>
      )}

      <div className="flex items-center space-x-2">
        <button
          className="p-2 hover:bg-accent rounded-lg transition-colors"
          onClick={() => setShowImageUpload(true)}
          title="Enviar imagem"
        >
          <Paperclip className="h-5 w-5 text-muted-foreground" />
        </button>

        <button
          className="p-2 hover:bg-accent rounded-lg transition-colors"
          onClick={() => setShowEmojiPicker(!showEmojiPicker)}
        >
          <Smile className="h-5 w-5 text-muted-foreground" />
        </button>

        <div className="flex-1 relative">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (pendingImage ? onSendPendingImage() : onSendMessage())}
            placeholder={isProcessingImage ? "Processando imagem..." : "Digite sua mensagem..."}
            disabled={isProcessingImage}
            className="w-full px-4 py-2 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent disabled:opacity-50"
          />

          {/* Indicador de processamento de imagem */}
          {isProcessingImage && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2 text-primary">
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs">Enviando imagem...</span>
            </div>
          )}

          {/* Emoji Picker */}
          {showEmojiPicker && (
            <div className="absolute bottom-full left-0 mb-2 z-50 emoji-picker-container">
              <EmojiPicker
                onSelect={onEmojiSelect}
                onClose={() => setShowEmojiPicker(false)}
              />
            </div>
          )}
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={pendingImage ? onSendPendingImage : onSendMessage}
          disabled={isProcessingImage || (!message.trim() && !pendingImage)}
          className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Send className="h-5 w-5" />
        </motion.button>
      </div>
    </div>
  )
}

export default MessageInput;

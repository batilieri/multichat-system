import React from 'react'
import { motion } from 'framer-motion'
import { Heart } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription
} from '../ui/dialog'
import Message from '../Message'

const FavoritesModal = ({ 
  open, 
  onOpenChange, 
  favoritedMessages, 
  onScrollToMessage 
}) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-full h-[90vh] p-0 md:p-8 flex flex-col justify-center items-center">
        <DialogTitle asChild>
          <h2 className="text-2xl font-bold text-foreground flex items-center gap-2 mb-2">
            <Heart className="w-6 h-6 text-yellow-500" /> Mensagens Favoritas
          </h2>
        </DialogTitle>
        <DialogDescription asChild>
          <p className="text-muted-foreground mb-6">
            Suas mensagens favoritas nesta conversa. Clique em uma para ir até ela no chat.
          </p>
        </DialogDescription>
        <div className="overflow-y-auto h-full w-full flex flex-col gap-4 px-2 md:px-0">
          {favoritedMessages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <Heart className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
              <p className="text-muted-foreground text-lg font-medium">Nenhuma mensagem favorita</p>
              <p className="text-muted-foreground/70 text-sm mt-2">
                Toque na estrela ⭐ em qualquer mensagem para favoritá-la
              </p>
            </motion.div>
          ) : (
            favoritedMessages.map((msg, index) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.01 }}
                className="w-full cursor-pointer hover:bg-accent/50 rounded-lg transition-colors border border-border/50"
                onClick={() => onScrollToMessage(msg.id)}
              >
                <div className="p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-muted-foreground">
                      {new Date(msg.timestamp).toLocaleDateString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                    <Heart className="w-4 h-4 text-yellow-500" />
                  </div>
                  <Message message={msg} hideMenu />
                </div>
              </motion.div>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default FavoritesModal;

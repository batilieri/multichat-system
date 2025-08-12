import React from 'react'
import { motion } from 'framer-motion'
import { Pin } from 'lucide-react'
import {
  Dialog,
  DialogContent
} from '../ui/dialog'
import Message from '../Message'

const PinnedMessagesModal = ({ 
  open, 
  onOpenChange, 
  pinnedMessages, 
  onScrollToMessage 
}) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="!fixed !z-50 !w-[80vw] !h-[80vh] !max-w-none !max-h-none !translate-x-[-50%] !translate-y-[-50%] !top-[50%] !left-[50%] p-0 overflow-hidden bg-background rounded-lg border border-border shadow-2xl [&>button]:!absolute [&>button]:!top-6 [&>button]:!right-6 [&>button]:!text-primary-foreground [&>button]:!hover:bg-primary-foreground/20 [&>button]:!bg-transparent [&>button]:!border-none [&>button]:!shadow-none [&>button]:!rounded-lg [&>button]:!p-2 [&>button]:!transition-colors">
        <div className="bg-primary text-primary-foreground p-6 border-b border-primary/20">
          <div className="flex items-center gap-2">
            <Pin className="w-6 h-6 text-primary-foreground" />
            <h2 className="text-2xl font-bold">Mensagens fixadas</h2>
          </div>
          <p className="text-primary-foreground/80 text-sm mt-1">
            Veja todas as mensagens fixadas nesta conversa. Clique em uma para ir até ela no chat.
          </p>
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto flex flex-col gap-4">
            {pinnedMessages.length === 0 && (
              <div className="text-muted-foreground text-sm">Nenhuma mensagem fixada.</div>
            )}
            {pinnedMessages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.01 }}
                className="w-full cursor-pointer hover:bg-accent/50 rounded-lg transition-colors"
                onClick={() => onScrollToMessage(msg.id)}
              >
                <Message message={msg} hideMenu />
              </motion.div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default PinnedMessagesModal;

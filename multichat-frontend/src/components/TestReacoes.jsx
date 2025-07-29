import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { SmilePlus } from 'lucide-react'
import { Popover, PopoverTrigger, PopoverContent } from './ui/popover'
import { EmojiReactionBar } from './EmojiReactionBar'
import EmojiPicker from './EmojiPicker'

const TestReacoes = () => {
  const [showReactionPopover, setShowReactionPopover] = useState(false)
  const [showFullPicker, setShowFullPicker] = useState(false)
  const [reactions, setReactions] = useState([])
  const [anchorRect, setAnchorRect] = useState(null)
  const [popoverSide, setPopoverSide] = useState('top')
  const [popoverAlign, setPopoverAlign] = useState('start')

  const handleReact = () => {
    // Simular posicionamento do popover
    const rect = { top: 100, left: 200, bottom: 150, right: 250 }
    setAnchorRect(rect)
    setPopoverSide('bottom')
    setPopoverAlign('start')
    setShowReactionPopover(true)
    setShowFullPicker(false)
  }

  const handleAddReaction = (emoji) => {
    if (reactions.includes(emoji)) {
      setReactions(prev => prev.filter(r => r !== emoji))
    } else {
      setReactions(prev => [...prev, emoji])
    }
    setShowReactionPopover(false)
    setShowFullPicker(false)
  }

  return (
    <div className="p-8 bg-background min-h-screen">
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">🧪 Teste do Sistema de Reações</h1>
        
        {/* Mensagem de teste */}
        <div className="bg-card border border-border rounded-lg p-4 mb-4">
          <p className="text-foreground mb-2">Olá! Esta é uma mensagem de teste para verificar as reações.</p>
          
          {/* Reações existentes */}
          {reactions.length > 0 && (
            <div className="flex gap-1 mb-3">
              {reactions.map((reaction, index) => (
                <span key={index} className="text-lg">{reaction}</span>
              ))}
            </div>
          )}
          
          {/* Botão de reações */}
          <div className="flex justify-between items-center">
            <Popover open={showReactionPopover} onOpenChange={setShowReactionPopover}>
              <PopoverTrigger asChild>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleReact}
                  className="p-2 rounded-full hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
                  title="Adicionar reação"
                >
                  <SmilePlus className="w-4 h-4 text-muted-foreground" />
                </motion.button>
              </PopoverTrigger>
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
                    isReversed={false}
                  />
                ) : (
                  <EmojiPicker
                    onSelect={emoji => { 
                      handleAddReaction(emoji); 
                      setShowReactionPopover(false); 
                      setShowFullPicker(false) 
                    }}
                    onClose={() => { setShowFullPicker(false) }}
                  />
                )}
              </PopoverContent>
            </Popover>
            
            <span className="text-xs text-muted-foreground">
              {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
        
        {/* Informações de debug */}
        <div className="bg-muted p-4 rounded-lg">
          <h3 className="font-semibold mb-2">📊 Debug Info:</h3>
          <p><strong>Reações atuais:</strong> {reactions.join(' ')}</p>
          <p><strong>Popover aberto:</strong> {showReactionPopover ? 'Sim' : 'Não'}</p>
          <p><strong>Picker completo:</strong> {showFullPicker ? 'Sim' : 'Não'}</p>
          <p><strong>Total de reações:</strong> {reactions.length}</p>
        </div>
      </div>
    </div>
  )
}

export default TestReacoes 
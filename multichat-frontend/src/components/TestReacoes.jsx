import React, { useState } from 'react'
import { SmilePlus } from 'lucide-react'
import { EmojiReactionBar } from './EmojiReactionBar'

const TestReacoes = () => {
  const [reactions, setReactions] = useState([])
  const [showReactionPopover, setShowReactionPopover] = useState(false)

  const handleAddReaction = (emoji) => {
    console.log('🎯 Adicionando reação:', emoji)
    if (reactions.includes(emoji)) {
      setReactions(prev => prev.filter(r => r !== emoji))
    } else {
      setReactions(prev => [...prev, emoji])
    }
  }

  return (
    <div className="p-8 space-y-4">
      <h1 className="text-2xl font-bold">🧪 Teste de Reações</h1>
      
      {/* Botão de teste */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setShowReactionPopover(!showReactionPopover)}
          className="p-2 rounded-full hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
          title="Adicionar reação"
        >
          <SmilePlus className="w-6 h-6 text-muted-foreground" />
        </button>
        
        <span className="text-sm text-muted-foreground">
          Clique no botão para testar as reações
        </span>
      </div>

      {/* Popover simples */}
      {showReactionPopover && (
        <div className="bg-popover border border-border p-3 rounded-xl shadow-lg max-h-[60vh] overflow-y-auto">
          <EmojiReactionBar
            onSelect={handleAddReaction}
            onOpenFullPicker={() => console.log('Abrir picker completo')}
            isReversed={false}
          />
        </div>
      )}

      {/* Exibir reações */}
      {reactions.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold">Reações atuais:</h3>
          <div className="flex flex-wrap gap-2">
            {reactions.map((reaction, index) => (
              <div
                key={index}
                className="w-8 h-8 flex items-center justify-center rounded-full bg-primary-foreground/20 border border-border text-primary-foreground"
              >
                {reaction}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Debug info */}
      <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <h3 className="font-semibold mb-2">Debug Info:</h3>
        <p><strong>Reações atuais:</strong> {reactions.join(' ')}</p>
        <p><strong>Total de reações:</strong> {reactions.length}</p>
        <p><strong>Popover aberto:</strong> {showReactionPopover ? 'Sim' : 'Não'}</p>
      </div>
    </div>
  )
}

export default TestReacoes 
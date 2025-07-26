import React from 'react'
import { motion } from 'framer-motion'
import Emoji from './Emoji'

const EmojiReactionBar = ({ onSelect, onOpenFullPicker, isReversed = false }) => {
  const commonEmojis = ['👍', '❤️', '😂', '😮', '😢', '😡']

  return (
    <div className={`flex gap-1 items-center ${isReversed ? 'flex-row-reverse' : ''}`}>
      {commonEmojis.map((emoji, index) => (
        <motion.button
          key={index}
          whileHover={{ scale: 1.2 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => onSelect(emoji)}
          className="h-8 w-8 p-1.5 hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none rounded-md transition-colors text-base"
          aria-label={`Reagir com ${emoji}`}
          tabIndex={0}
          type="button"
        >
          <Emoji>{emoji}</Emoji>
        </motion.button>
      ))}
      <motion.button
        whileHover={{ scale: 1.2 }}
        whileTap={{ scale: 0.9 }}
        onClick={onOpenFullPicker}
        className={`h-8 w-8 p-1.5 hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none rounded-md transition-colors text-muted-foreground border border-border ${
          isReversed ? 'mr-1' : 'ml-1'
        }`}
        aria-label="Abrir seletor completo de emojis"
        tabIndex={0}
        type="button"
      >
        +
      </motion.button>
    </div>
  )
}

export { EmojiReactionBar } 
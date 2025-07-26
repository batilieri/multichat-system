import React from 'react'
import Emoji from './Emoji'

export default function EmojiBadge({ children, onClick, title, label, className = '', ...props }) {
  return (
    <button
      type="button"
      className={`w-8 h-8 flex items-center justify-center rounded-full bg-primary-foreground/20 border border-border text-primary-foreground cursor-pointer transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:bg-accent ${className}`}
      onClick={onClick}
      title={title}
      aria-label={label || title}
      {...props}
    >
      <Emoji size="1.1rem">{children}</Emoji>
    </button>
  )
} 
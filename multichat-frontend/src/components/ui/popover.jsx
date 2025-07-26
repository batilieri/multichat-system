import React, { useState, useRef, useEffect } from 'react'
import ReactDOM from 'react-dom'

const Popover = ({ children, open, onOpenChange }) => {
  return (
    <div className="relative">
      {React.Children.map(children, child => {
        if (
          React.isValidElement(child) &&
          typeof child.type === 'function' // só componentes customizados
        ) {
          return React.cloneElement(child, { open, onOpenChange })
        }
        return child
      })}
    </div>
  )
}

const PopoverTrigger = ({ children, asChild = false, open, onOpenChange }) => {
  const triggerRef = useRef(null)
  const [isOpen, setIsOpen] = useState(false)

  const handleClick = () => {
    const newState = !isOpen
    setIsOpen(newState)
    if (onOpenChange) {
      onOpenChange(newState)
    }
  }

  useEffect(() => {
    setIsOpen(open || false)
  }, [open])

  if (asChild) {
    return React.cloneElement(children, {
      ref: triggerRef,
      onClick: handleClick
    })
  }

  return (
    <div ref={triggerRef} onClick={handleClick}>
      {children}
    </div>
  )
}

const PopoverContent = ({
  children,
  className = "",
  anchorRect = null,
  onClose,
  ...props
}) => {
  const contentRef = React.useRef(null)
  const [position, setPosition] = React.useState({ top: 0, left: 0 })

  React.useEffect(() => {
    if (anchorRect && contentRef.current) {
      const popover = contentRef.current
      const popoverRect = popover.getBoundingClientRect()
      let top = anchorRect.bottom + 8 // 8px de espaçamento
      let left = anchorRect.left
      // Se não cabe para baixo, abre para cima
      if (top + popoverRect.height > window.innerHeight) {
        top = anchorRect.top - popoverRect.height - 8
      }
      // Se não cabe para a direita, ajusta para a esquerda
      if (left + popoverRect.width > window.innerWidth) {
        left = window.innerWidth - popoverRect.width - 8
      }
      // Nunca deixa negativo
      top = Math.max(8, top)
      left = Math.max(8, left)
      setPosition({ top, left })
    }
  }, [anchorRect, children])

  React.useEffect(() => {
    function handleClickOutside(event) {
      if (contentRef.current && !contentRef.current.contains(event.target)) {
        if (onClose) onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  if (!anchorRect) return null
  return ReactDOM.createPortal(
    <div
      ref={contentRef}
      className={"fixed z-50 " + className}
      style={{ top: position.top, left: position.left, minWidth: 220, maxWidth: 360, ...props.style }}
      {...props}
    >
      {children}
    </div>,
    document.body
  )
}

export { Popover, PopoverTrigger, PopoverContent }

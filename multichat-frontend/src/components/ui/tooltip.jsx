import React, { useState } from 'react'

const Tooltip = ({ children, content, className = "" }) => {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div
      className={`relative inline-block ${className}`}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className="absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-md shadow-lg whitespace-nowrap -top-2 left-1/2 transform -translate-x-1/2 -translate-y-full">
          {content}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  )
}

const TooltipTrigger = ({ children }) => children
const TooltipContent = ({ children }) => children

export { Tooltip, TooltipTrigger, TooltipContent }

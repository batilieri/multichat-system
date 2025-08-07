import React, { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Download, ZoomIn, ZoomOut, RotateCw } from 'lucide-react'

export const ImageModal = ({ isOpen, imageUrl, onClose, imageAlt = "Imagem" }) => {
  const [scale, setScale] = React.useState(1)
  const [rotation, setRotation] = React.useState(0)

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  useEffect(() => {
    if (isOpen) {
      setScale(1)
      setRotation(0)
    }
  }, [isOpen])

  const handleZoomIn = () => setScale(prev => Math.min(prev + 0.25, 3))
  const handleZoomOut = () => setScale(prev => Math.max(prev - 0.25, 0.25))
  const handleRotate = () => setRotation(prev => prev + 90)
  const handleDownload = () => {
    if (imageUrl) {
      const link = document.createElement('a')
      link.href = imageUrl
      link.download = `image_${Date.now()}.jpg`
      link.click()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
          onClick={onClose}
        >
          {/* Container da imagem */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="relative max-w-[90vw] max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Imagem */}
            <img
              src={imageUrl}
              alt={imageAlt}
              className="max-w-full max-h-full object-contain"
              style={{
                transform: `scale(${scale}) rotate(${rotation}deg)`,
                transition: 'transform 0.3s ease'
              }}
            />

            {/* Controles */}
            <div className="absolute top-4 right-4 flex gap-2">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleZoomIn}
                className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors"
                title="Aumentar zoom"
              >
                <ZoomIn className="w-4 h-4" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleZoomOut}
                className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors"
                title="Diminuir zoom"
              >
                <ZoomOut className="w-4 h-4" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleRotate}
                className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors"
                title="Rotacionar"
              >
                <RotateCw className="w-4 h-4" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleDownload}
                className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors"
                title="Baixar imagem"
              >
                <Download className="w-4 h-4" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors"
                title="Fechar"
              >
                <X className="w-4 h-4" />
              </motion.button>
            </div>

            {/* Indicador de zoom */}
            <div className="absolute bottom-4 left-4 bg-black/80 text-white px-3 py-1 rounded-full text-sm">
              {Math.round(scale * 100)}%
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 
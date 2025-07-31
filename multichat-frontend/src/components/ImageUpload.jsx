import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, X, Image as ImageIcon, Copy, Check } from 'lucide-react'
import { toast } from './ui/use-toast'

const ImageUpload = ({ onImageSelect, onClose, isVisible }) => {
  const [dragActive, setDragActive] = useState(false)
  const [clipboardImage, setClipboardImage] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [uploadMethod, setUploadMethod] = useState('clipboard') // 'clipboard' | 'file' | 'url'
  const [imageUrl, setImageUrl] = useState('')
  const fileInputRef = useRef(null)

  // Detectar imagens no clipboard
  useEffect(() => {
    const handlePaste = async (event) => {
      const items = event.clipboardData?.items
      if (!items) return

      for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
          const file = item.getAsFile()
          if (file) {
            const reader = new FileReader()
            reader.onload = (e) => {
              setClipboardImage({
                file: file,
                preview: e.target.result,
                name: `clipboard-${Date.now()}.png`
              })
              setUploadMethod('clipboard')
            }
            reader.readAsDataURL(file)
            break
          }
        }
      }
    }

    if (isVisible) {
      document.addEventListener('paste', handlePaste)
      return () => document.removeEventListener('paste', handlePaste)
    }
  }, [isVisible])

  // Converter imagem para Base64
  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        // Remover o prefixo "data:image/...;base64," para obter apenas o Base64
        const base64 = reader.result.split(',')[1]
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  // Enviar imagem
  const handleSendImage = async () => {
    if (!clipboardImage && !imageUrl) {
      toast({
        title: "❌ Erro",
        description: "Selecione uma imagem primeiro",
        duration: 3000,
      })
      return
    }

    setIsLoading(true)

    try {
      let imageData = null

      if (uploadMethod === 'clipboard' && clipboardImage) {
        // Converter imagem do clipboard para Base64
        const base64 = await convertToBase64(clipboardImage.file)
        imageData = {
          type: 'base64',
          data: base64,
          filename: clipboardImage.name
        }
      } else if (uploadMethod === 'url' && imageUrl) {
        // Usar URL da imagem
        imageData = {
          type: 'url',
          data: imageUrl,
          filename: 'image-from-url.jpg'
        }
      } else if (uploadMethod === 'file' && clipboardImage) {
        // Converter arquivo para Base64
        const base64 = await convertToBase64(clipboardImage.file)
        imageData = {
          type: 'base64',
          data: base64,
          filename: clipboardImage.name
        }
      }

      if (imageData) {
        onImageSelect(imageData)
        toast({
          title: "✅ Imagem pronta",
          description: "Imagem preparada para envio",
          duration: 2000,
        })
        onClose()
      }
    } catch (error) {
      console.error('❌ Erro ao processar imagem:', error)
      toast({
        title: "❌ Erro",
        description: "Erro ao processar a imagem",
        duration: 4000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Lidar com drag and drop
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setClipboardImage({
            file: file,
            preview: e.target.result,
            name: file.name
          })
          setUploadMethod('file')
        }
        reader.readAsDataURL(file)
      }
    }
  }

  // Lidar com seleção de arquivo
  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setClipboardImage({
          file: file,
          preview: e.target.result,
          name: file.name
        })
        setUploadMethod('file')
      }
      reader.readAsDataURL(file)
    }
  }

  // Copiar imagem para clipboard
  const copyToClipboard = async () => {
    if (clipboardImage) {
      try {
        const blob = await fetch(clipboardImage.preview).then(r => r.blob())
        await navigator.clipboard.write([
          new ClipboardItem({
            [blob.type]: blob
          })
        ])
        toast({
          title: "✅ Copiado",
          description: "Imagem copiada para clipboard",
          duration: 2000,
        })
      } catch (error) {
        console.error('❌ Erro ao copiar:', error)
        toast({
          title: "❌ Erro",
          description: "Erro ao copiar imagem",
          duration: 3000,
        })
      }
    }
  }

  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
    >
      <motion.div
        initial={{ y: 50 }}
        animate={{ y: 0 }}
        className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-xl max-w-md w-full mx-4"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Enviar Imagem</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-zinc-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Métodos de upload */}
        <div className="mb-4">
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setUploadMethod('clipboard')}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                uploadMethod === 'clipboard'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
              }`}
            >
              <Copy className="w-4 h-4 mr-2 inline" />
              Clipboard
            </button>
            <button
              onClick={() => setUploadMethod('file')}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                uploadMethod === 'file'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
              }`}
            >
              <Upload className="w-4 h-4 mr-2 inline" />
              Arquivo
            </button>
            <button
              onClick={() => setUploadMethod('url')}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                uploadMethod === 'url'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
              }`}
            >
              <ImageIcon className="w-4 h-4 mr-2 inline" />
              URL
            </button>
          </div>
        </div>

        {/* Área de upload */}
        {uploadMethod === 'clipboard' && (
          <div className="mb-4">
            <div className="border-2 border-dashed border-gray-300 dark:border-zinc-600 rounded-lg p-6 text-center">
              <Copy className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Cole uma imagem (Ctrl+V) ou arraste uma imagem aqui
              </p>
              {clipboardImage && (
                <div className="mt-4">
                  <img
                    src={clipboardImage.preview}
                    alt="Preview"
                    className="max-w-full h-32 object-contain rounded-lg"
                  />
                  <p className="text-xs text-gray-500 mt-2">{clipboardImage.name}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {uploadMethod === 'file' && (
          <div className="mb-4">
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                dragActive
                  ? 'border-primary bg-primary/10'
                  : 'border-gray-300 dark:border-zinc-600'
              }`}
            >
              <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Arraste uma imagem aqui ou clique para selecionar
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm"
              >
                Selecionar Arquivo
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              {clipboardImage && (
                <div className="mt-4">
                  <img
                    src={clipboardImage.preview}
                    alt="Preview"
                    className="max-w-full h-32 object-contain rounded-lg"
                  />
                  <p className="text-xs text-gray-500 mt-2">{clipboardImage.name}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {uploadMethod === 'url' && (
          <div className="mb-4">
            <input
              type="url"
              placeholder="Cole a URL da imagem aqui"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-zinc-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            {imageUrl && (
              <div className="mt-4">
                <img
                  src={imageUrl}
                  alt="Preview"
                  className="max-w-full h-32 object-contain rounded-lg"
                  onError={() => {
                    toast({
                      title: "❌ Erro",
                      description: "URL da imagem inválida",
                      duration: 3000,
                    })
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* Ações */}
        <div className="flex gap-2">
          {clipboardImage && (
            <button
              onClick={copyToClipboard}
              className="flex-1 px-4 py-2 bg-gray-100 dark:bg-zinc-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-zinc-700 transition-colors"
            >
              <Copy className="w-4 h-4 mr-2 inline" />
              Copiar
            </button>
          )}
          <button
            onClick={handleSendImage}
            disabled={isLoading || (!clipboardImage && !imageUrl)}
            className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Processando...
              </>
            ) : (
              <>
                <Check className="w-4 h-4 mr-2 inline" />
                Enviar
              </>
            )}
          </button>
        </div>

        {/* Instruções */}
        <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
          <p>💡 Dica: Use Ctrl+V para colar imagens do clipboard</p>
          <p>📁 Formatos suportados: PNG, JPEG, JPG</p>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default ImageUpload 
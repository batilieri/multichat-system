import React from 'react'
import { X } from 'lucide-react'

const PendingImagePreview = ({ 
  pendingImage, 
  setPendingImage, 
  imageCaption, 
  setImageCaption 
}) => {
  if (!pendingImage) return null;

  return (
    <div className="mb-3 p-3 bg-accent/30 border border-border rounded-lg">
      <div className="flex items-start gap-3">
        <img
          src={`data:image/png;base64,${pendingImage.data}`}
          alt="Imagem para enviar"
          className="w-16 h-16 object-cover rounded-lg"
        />
        <div className="flex-1">
          <div className="text-sm text-muted-foreground mb-2">Imagem pronta para enviar</div>
          <input
            type="text"
            value={imageCaption}
            onChange={(e) => setImageCaption(e.target.value)}
            placeholder="Legenda (opcional)"
            className="w-full px-3 py-2 text-sm border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          onClick={() => setPendingImage(null)}
          className="p-1 rounded-full hover:bg-accent transition-colors"
          title="Cancelar"
        >
          <X className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>
    </div>
  )
}

export default PendingImagePreview;

import React from 'react'

const ImageModal = ({ 
  showImageModal, 
  setShowImageModal, 
  imageSrc, 
  imageAlt 
}) => {
  if (!showImageModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={() => setShowImageModal(false)}>
      <img
        src={imageSrc}
        alt={imageAlt || "Imagem"}
        className="max-h-[80vh] max-w-[90vw] rounded-xl shadow-2xl border-4 border-white"
        onClick={e => e.stopPropagation()}
      />
      <button
        className="absolute top-6 right-8 text-white text-3xl font-bold bg-black/60 rounded-full px-3 py-1 hover:bg-black/80 transition"
        onClick={() => setShowImageModal(false)}
        style={{ zIndex: 100 }}
      >
        ×
      </button>
    </div>
  )
}

export default ImageModal;

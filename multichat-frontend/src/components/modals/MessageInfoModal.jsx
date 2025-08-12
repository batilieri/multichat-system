import React from 'react'
import {
  Info,
  CheckCheck,
  Play
} from 'lucide-react'

const MessageInfoModal = ({ 
  infoModalMessage, 
  onClose 
}) => {
  if (!infoModalMessage) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-background dark:bg-zinc-900 rounded-xl p-6 shadow-xl min-w-[340px] max-w-[90vw]">
        <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
          <Info className="w-5 h-5" /> Dados da mensagem
        </h2>
        <div className="space-y-4">
          {/* Status: Entregue */}
          <div className="flex items-center gap-3">
            <CheckCheck className="w-5 h-5 text-muted-foreground" />
            <div>
              <div className="font-medium">Entregue</div>
              <div className="text-xs text-muted-foreground">
                {infoModalMessage.entregueEm ? `Hoje às ${infoModalMessage.entregueEm}` : '—'}
              </div>
            </div>
          </div>
          
          {/* Status: Vista */}
          <div className="flex items-center gap-3">
            <CheckCheck className="w-5 h-5 text-primary" />
            <div>
              <div className="font-medium">Vista</div>
              <div className="text-xs text-muted-foreground">
                {infoModalMessage.vistaEm ? `Hoje às ${infoModalMessage.vistaEm}` : '—'}
              </div>
            </div>
          </div>
          
          {/* Status: Reproduzida (apenas para áudio) */}
          {infoModalMessage.tipo === 'audio' && (
            <div className="flex items-center gap-3">
              <Play className="w-5 h-5 text-blue-500" />
              <div>
                <div className="font-medium">Reproduzida</div>
                <div className="text-xs text-muted-foreground">
                  {infoModalMessage.reproduzidaEm ? `Hoje às ${infoModalMessage.reproduzidaEm}` : '—'}
                </div>
              </div>
            </div>
          )}
        </div>
        <button 
          className="mt-6 px-4 py-2 rounded bg-primary text-primary-foreground w-full" 
          onClick={onClose}
        >
          Fechar
        </button>
      </div>
    </div>
  )
}

export default MessageInfoModal;

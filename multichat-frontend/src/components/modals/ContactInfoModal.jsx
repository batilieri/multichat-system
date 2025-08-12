import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Phone,
  Video,
  Star,
  Edit,
  Volume2,
  VolumeX,
  Bookmark
} from 'lucide-react'
import {
  Dialog,
  DialogContent
} from '../ui/dialog'
import { Button } from '../ui/button'

const ContactInfoModal = React.memo(({ open, onOpenChange, contactInfo, onClose, chat, setShowImageModal }) => {
  const [editingName, setEditingName] = useState(false);
  const [editedName, setEditedName] = useState(contactInfo?.name || '');
  const [isMuted, setIsMuted] = useState(contactInfo?.isMuted || false);
  const [isStarred, setIsStarred] = useState(contactInfo?.isStarred || false);
  const [notificationSound, setNotificationSound] = useState(true);

  // Atualizar estados locais quando contactInfo mudar
  useEffect(() => {
    if (contactInfo) {
      setEditedName(contactInfo.name || '');
      setIsMuted(contactInfo.isMuted || false);
      setIsStarred(contactInfo.isStarred || false);
    }
  }, [contactInfo]);

  function saveName(newName) {
    console.log("Salvando nome:", newName);
    // Não modificar diretamente o contactInfo, apenas o estado local
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      alert("Número copiado!");
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-full h-[90vh] p-0 md:p-8 flex flex-col justify-center items-center rounded-lg border border-border shadow-2xl bg-background overflow-hidden">

        {/* Topo estilo WhatsApp: Foto + Nome + botão editar */}
        <div className="flex items-center w-full mb-6 px-4 md:px-0">
          <div
            className="h-20 w-20 rounded-full overflow-hidden mr-4 cursor-pointer flex-shrink-0"
            onClick={e => {
              e.stopPropagation();
              if (chat?.foto_perfil || chat?.profile_picture) setShowImageModal(true);
            }}
            title="Clique para ampliar a foto"
          >
            {chat?.foto_perfil || chat?.profile_picture ? (
              <img
                src={chat.foto_perfil || chat.profile_picture}
                alt={contactInfo?.name || 'Contato'}
                className="h-full w-full object-cover"
                onError={e => {
                  e.target.style.display = 'none';
                  e.target.nextSibling && (e.target.nextSibling.style.display = 'flex');
                }}
              />
            ) : (
              <svg
                width="80"
                height="80"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
                className="h-full w-full text-primary-foreground"
              >
                <circle cx="12" cy="7" r="4" />
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
              </svg>
            )}
          </div>

          <div className="flex flex-col flex-1 min-w-0">
            {!editingName ? (
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-semibold text-foreground truncate">
                  {contactInfo?.name || 'Contato'}
                </h2>
                <Button variant="ghost" size="sm" onClick={() => setEditingName(true)}>
                  Editar
                </Button>
              </div>
            ) : (
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={editedName}
                  onChange={e => setEditedName(e.target.value)}
                  className="input input-bordered w-full max-w-xs"
                  autoFocus
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    saveName(editedName);
                    setEditingName(false);
                  }}
                >
                  Salvar
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setEditingName(false);
                    setEditedName(contactInfo?.name || '');
                  }}
                >
                  Cancelar
                </Button>
              </div>
            )}

            {/* Número do contato destacado */}
            <p
              className="mt-1 text-lg font-semibold cursor-pointer select-text text-blue-600"
              onClick={() => copyToClipboard(contactInfo?.phone || '')}
              title="Clique para copiar o número do contato"
            >
              {contactInfo?.phone || 'N/A'}
            </p>
          </div>
        </div>

        <div className="overflow-y-auto h-full w-full flex flex-col gap-8 px-4 md:px-0">

          {/* Funções Rápidas */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">
              Funções Rápidas
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Button variant="outline" className="w-full justify-start h-14 text-base" onClick={() => alert("Chamada de áudio")}>
                <Phone className="h-5 w-5 mr-3" />
                Chamada de áudio
              </Button>
              <Button variant="outline" className="w-full justify-start h-14 text-base" onClick={() => alert("Chamada de vídeo")}>
                <Video className="h-5 w-5 mr-3" />
                Chamada de vídeo
              </Button>
              <Button variant="outline" className="w-full justify-start h-14 text-base" onClick={() => alert("Mensagens favoritas")}>
                <Star className="h-5 w-5 mr-3" />
                Mensagens favoritas
              </Button>
              <Button variant="outline" className="w-full justify-start h-14 text-base" onClick={() => alert("Mensagens fixadas")}>
                <Bookmark className="h-5 w-5 mr-3" />
                Mensagens fixadas
              </Button>
            </div>
          </motion.section>

          {/* Configurações de contato */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">
              Configurações de contato
            </h4>
            <div className="space-y-3">
              <Button
                variant={isStarred ? "primary" : "outline"}
                className="w-full justify-start h-14 text-base"
                onClick={() => setIsStarred(!isStarred)}
              >
                <Star className="h-5 w-5 mr-3" />
                {isStarred ? "Remover dos favoritos" : "Marcar favorito"}
              </Button>

              {/* Editar nome */}
              {!editingName ? (
                <Button variant="ghost" className="w-full justify-start h-14 text-base" onClick={() => setEditingName(true)}>
                  <Edit className="h-5 w-5 mr-3" />
                  Editar nome do contato
                </Button>
              ) : (
                <div className="flex space-x-2 mt-2">
                  <input
                    type="text"
                    value={editedName}
                    onChange={e => setEditedName(e.target.value)}
                    className="input input-bordered w-full"
                    autoFocus
                  />
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      saveName(editedName);
                      setEditingName(false);
                    }}
                  >
                    Salvar
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => {
                    setEditingName(false);
                    setEditedName(contactInfo?.name || '');
                  }}>
                    Cancelar
                  </Button>
                </div>
              )}
            </div>
          </motion.section>

          {/* Notificações */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">
              Notificações
            </h4>
            <div className="space-y-3">
              <Button
                variant={notificationSound ? "primary" : "outline"}
                className="w-full justify-start h-14 text-base"
                onClick={() => setNotificationSound(!notificationSound)}
              >
                <Volume2 className="h-5 w-5 mr-3" />
                Som de notificações {notificationSound ? "(Ligado)" : "(Desligado)"}
              </Button>

              <Button
                variant={isMuted ? "outline" : "primary"}
                className="w-full justify-start h-14 text-base"
                onClick={() => setIsMuted(!isMuted)}
              >
                <Volume2 className="h-5 w-5 mr-3" />
                {isMuted ? "Ativar notificações" : "Silenciar contato"}
              </Button>
            </div>
          </motion.section>
        </div>
      </DialogContent>
    </Dialog>
  );
});

ContactInfoModal.displayName = 'ContactInfoModal';

export default ContactInfoModal;

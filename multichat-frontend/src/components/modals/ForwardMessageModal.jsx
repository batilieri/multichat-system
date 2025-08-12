import React from 'react'

const ForwardMessageModal = ({ 
  forwardModalMessage, 
  forwardSearch, 
  setForwardSearch, 
  selectedChats, 
  filteredChats, 
  onSelectChat, 
  onConfirmForward, 
  onCloseForwardModal 
}) => {
  if (!forwardModalMessage) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-background rounded-xl shadow-2xl w-full max-w-md mx-auto p-0">
        <div className="flex items-center border-b border-border p-4">
          <button onClick={onCloseForwardModal} className="mr-2 p-1 rounded hover:bg-accent transition-colors">
            <span className="text-xl">×</span>
          </button>
          <h2 className="text-lg font-semibold">Encaminhar mensagem para</h2>
        </div>
        <div className="p-4">
          <div className="mb-4">
            <div className="flex items-center border border-primary rounded-lg px-3 py-2">
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" className="mr-2 text-primary">
                <circle cx="8" cy="8" r="7" />
                <line x1="13" y1="13" x2="17" y2="17" />
              </svg>
              <input
                type="text"
                placeholder="Buscar contato ou grupo"
                className="flex-1 bg-transparent outline-none text-foreground"
                value={forwardSearch}
                onChange={e => setForwardSearch(e.target.value)}
              />
            </div>
          </div>
          <div className="mb-2 text-sm text-primary font-medium">Conversas recentes</div>
          <div className="max-h-60 overflow-y-auto divide-y divide-border">
            {filteredChats.length === 0 && (
              <div className="text-muted-foreground text-sm p-4 text-center">Nenhum contato encontrado.</div>
            )}
            {filteredChats.map(chat => {
              const name = chat.is_group ? (chat.group_name || 'Grupo') : (chat.contact_name || chat.sender_name || chat.chat_id || 'Contato')
              const selected = selectedChats.includes(chat.id)
              return (
                <div
                  key={chat.id}
                  className={`flex items-center px-3 py-2 cursor-pointer hover:bg-accent transition-colors rounded ${selected ? 'bg-primary/10 border-l-4 border-primary' : ''}`}
                  onClick={() => onSelectChat(chat.id)}
                >
                  <div className="h-8 w-8 bg-accent rounded-full flex items-center justify-center mr-3">
                    {chat.is_group ? (
                      <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="10" cy="10" r="8" />
                        <path d="M6 14s1-2 4-2 4 2 4 2" />
                      </svg>
                    ) : (
                      <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="10" cy="10" r="8" />
                        <circle cx="10" cy="8" r="3" />
                        <path d="M6 16s1-2 4-2 4 2 4 2" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{name}</div>
                    <div className="text-xs text-muted-foreground">{chat.chat_id || 'N/A'}</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={() => onSelectChat(chat.id)}
                    className="accent-primary w-4 h-4 ml-2"
                    onClick={e => e.stopPropagation()}
                  />
                </div>
              )
            })}
          </div>
          <div className="flex justify-end mt-4">
            <button
              className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-semibold disabled:opacity-50"
              disabled={selectedChats.length === 0}
              onClick={onConfirmForward}
            >
              Encaminhar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ForwardMessageModal;

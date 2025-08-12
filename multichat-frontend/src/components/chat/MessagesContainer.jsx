import React from 'react'
import Message from '../Message'

const MessagesContainer = ({ 
  messages, 
  loading, 
  hasMore, 
  messageRefs, 
  messageGroups, 
  onScroll, 
  onLoadMore, 
  profilePicture,
  onReply,
  onForward,
  onShowInfo,
  onDelete
}) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 w-full messages-container" onScroll={onScroll}>
      {!loading && Object.entries(messageGroups).map(([date, msgs]) => (
        <div key={date} className="w-full">
          <div className="flex justify-center my-2">
            <span className="bg-muted text-xs px-3 py-1 rounded-full border border-border">{date}</span>
          </div>
          <div className="flex flex-col gap-2">
            {msgs.map((msg) => (
              <div key={msg.id} className="w-full" ref={el => messageRefs.current[msg.id] = el}>
                <Message
                  message={msg}
                  profilePicture={profilePicture}
                  onReply={onReply}
                  onForward={onForward}
                  onShowInfo={onShowInfo}
                  onDelete={onDelete}
                />
              </div>
            ))}
          </div>
        </div>
      ))}
      
      {loading && <div className="text-center text-muted-foreground">Carregando mensagens...</div>}
      
      {hasMore && !loading && (
        <div className="flex justify-center my-2">
          <button className="text-xs text-primary underline" onClick={onLoadMore}>
            Carregar mais mensagens
          </button>
        </div>
      )}
    </div>
  )
}

export default MessagesContainer;

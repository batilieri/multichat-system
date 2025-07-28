import React, { createContext, useContext, useEffect, useState } from 'react'
import { useGlobalUpdates } from '../hooks/use-realtime-updates'

const RealtimeContext = createContext()

export const useRealtime = () => {
  const context = useContext(RealtimeContext)
  if (!context) {
    throw new Error('useRealtime deve ser usado dentro de um RealtimeProvider')
  }
  return context
}

export const RealtimeProvider = ({ children }) => {
  const [globalUpdates, setGlobalUpdates] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)

  // Função para lidar com atualizações globais
  const handleGlobalUpdate = (update) => {
    console.log('🌐 Atualização global recebida no contexto:', update)
    
    setGlobalUpdates(prev => [...prev, update])
    setLastUpdate(new Date().toISOString())
    
    // Manter apenas as últimas 50 atualizações
    if (globalUpdates.length > 50) {
      setGlobalUpdates(prev => prev.slice(-50))
    }
  }

  // Usar hook de atualizações globais
  const { isConnected: realtimeConnected } = useGlobalUpdates(handleGlobalUpdate)

  // Atualizar status de conexão
  useEffect(() => {
    setIsConnected(realtimeConnected)
  }, [realtimeConnected])

  const value = {
    globalUpdates,
    isConnected,
    lastUpdate,
    clearUpdates: () => setGlobalUpdates([])
  }

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  )
} 
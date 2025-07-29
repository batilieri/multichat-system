/**
 * Serviço WebSocket para atualizações em tempo real
 * Substitui o polling quando disponível
 */
class WebSocketService {
  constructor() {
    this.ws = null
    this.callbacks = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.isConnecting = false
    this.isConnected = false
  }

  connect(chatId) {
    if (this.isConnecting || this.isConnected) return

    this.isConnecting = true
    const wsUrl = `ws://localhost:8000/ws/chat/${chatId}/`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('🔌 WebSocket conectado para chat:', chatId)
        this.isConnected = true
        this.isConnecting = false
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('❌ Erro ao processar mensagem WebSocket:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('🔌 WebSocket desconectado')
        this.isConnected = false
        this.isConnecting = false
        this.attemptReconnect()
      }
      
      this.ws.onerror = (error) => {
        console.error('❌ Erro no WebSocket:', error)
        this.isConnected = false
        this.isConnecting = false
      }
    } catch (error) {
      console.error('❌ Erro ao conectar WebSocket:', error)
      this.isConnecting = false
    }
  }

  handleMessage(data) {
    console.log('📨 Mensagem WebSocket recebida:', data)
    
    if (data.type === 'new_message') {
      // Atualização em tempo real sem polling
      this.callbacks.get('message_update')?.(data.message)
    } else if (data.type === 'chat_updated') {
      this.callbacks.get('chat_update')?.(data)
    } else if (data.type === 'status_update') {
      this.callbacks.get('status_update')?.(data)
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('❌ Máximo de tentativas de reconexão atingido')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts), 30000)
    
    console.log(`🔄 Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts} em ${delay}ms`)
    
    setTimeout(() => {
      if (!this.isConnected) {
        this.connect()
      }
    }, delay)
  }

  subscribe(event, callback) {
    this.callbacks.set(event, callback)
  }

  unsubscribe(event) {
    this.callbacks.delete(event)
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isConnected = false
    this.isConnecting = false
    this.callbacks.clear()
  }

  isWebSocketAvailable() {
    return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// Instância global do serviço WebSocket
const webSocketService = new WebSocketService()

export default webSocketService 
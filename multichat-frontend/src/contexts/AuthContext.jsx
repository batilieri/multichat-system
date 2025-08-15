import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  // Verificar se há token salvo no localStorage - OTIMIZADO
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        let user = null;
        
        try {
          user = JSON.parse(localStorage.getItem("user") || "null");
        } catch (e) {
          user = null;
        }
        
        console.log('🔍 Carregando usuário do localStorage:', user);
        console.log('🔍 Token encontrado:', !!token);
        
        if (token && user) {
          setUser(user)
          setIsAuthenticated(true)
          
          // Verificar token em background (não bloquear o carregamento)
          setTimeout(() => {
            verifyToken(token)
          }, 100)
        }
      } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error)
        logout()
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const verifyToken = useCallback(async (token) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/verify/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('Token inválido')
      }

      const data = await response.json()
      if (!data.valid) {
        logout()
      }
    } catch (error) {
      console.error('Erro ao verificar token:', error)
      logout()
    }
  }, [])

  const login = useCallback(async (email, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Erro ao fazer login')
      }

      console.log('🔍 Dados recebidos do login:', data);
      console.log('🔍 Dados do usuário:', data.user);
      
      // Salvar tokens e dados do usuário
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))

      setUser(data.user)
      setIsAuthenticated(true)

      return { success: true, user: data.user }
    } catch (error) {
      console.error('Erro no login:', error)
      throw error
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  const refreshToken = useCallback(async () => {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) {
        console.warn('⚠️ Refresh token não encontrado, fazendo logout')
        logout()
        return null
      }

      console.log('🔄 Renovando token de acesso...')
      
      const response = await fetch('http://localhost:8000/api/auth/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh }),
      })

      const data = await response.json()

      if (!response.ok) {
        console.error('❌ Falha ao renovar token:', data)
        logout()
        return null
      }

      console.log('✅ Token renovado com sucesso')
      localStorage.setItem('access_token', data.access)
      
      // Se o refresh token foi rotacionado, atualizar também
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh)
      }
      
      return data.access
    } catch (error) {
      console.error('❌ Erro ao renovar token:', error)
      logout()
      return null
    }
  }, [logout])

  const updateProfile = useCallback(async (profileData) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/profile/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Erro ao atualizar perfil')
      }

      setUser(data.user)
      localStorage.setItem('user', JSON.stringify(data.user))

      return { success: true, user: data.user }
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error)
      throw error
    }
  }, [])

  const changePassword = useCallback(async (currentPassword, newPassword) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/change-password/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Erro ao alterar senha')
      }

      return { success: true }
    } catch (error) {
      console.error('Erro ao alterar senha:', error)
      throw error
    }
  }, [])

  // OTIMIZADO: apiRequest com cache, timeout e retry inteligente
  const apiRequest = useCallback(async (url, options = {}) => {
    let token = localStorage.getItem('access_token')
    let retryCount = 0
    const maxRetries = 2
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    // Garantir que a URL seja completa (incluir o backend)
    const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`

    // Adicionar timeout para evitar travamentos
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 15000) // Aumentado para 15 segundos

    const makeRequest = async (useNewToken = false) => {
      try {
        let currentToken = token
        
        if (useNewToken) {
          const newToken = await refreshToken()
          if (newToken) {
            currentToken = newToken
            headers.Authorization = `Bearer ${newToken}`
          } else {
            throw new Error('Falha ao renovar token')
          }
        }

        const response = await fetch(fullUrl, {
          ...options,
          headers,
          signal: controller.signal,
        })

        // Se o token expirou e ainda não tentamos renovar
        if (response.status === 401 && !useNewToken && retryCount < maxRetries) {
          retryCount++
          console.log(`🔄 Token expirado, tentando renovar (tentativa ${retryCount}/${maxRetries})...`)
          return await makeRequest(true)
        }

        return response
      } catch (error) {
        if (error.name === 'AbortError') {
          throw new Error('Timeout na requisição')
        }
        throw error
      }
    }

    try {
      const response = await makeRequest()
      clearTimeout(timeoutId)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      throw error
    }
  }, [refreshToken])

  // Funções para verificar permissões - OTIMIZADAS com useCallback
  const isAdmin = useCallback(() => {
    return user && (user.is_superuser || user.tipo_usuario === 'admin')
  }, [user])

  const isCliente = useCallback(() => {
    return user && user.tipo_usuario === 'cliente'
  }, [user])

  const isColaborador = useCallback(() => {
    return user && user.tipo_usuario === 'colaborador'
  }, [user])

  const canCreateUsers = useCallback(() => {
    return isAdmin() || isCliente()
  }, [isAdmin, isCliente])

  const canAccessReports = useCallback(() => {
    return isAdmin() || isCliente()
  }, [isAdmin, isCliente])

  const canAccessSettings = useCallback(() => {
    return isAdmin() || isCliente()
  }, [isAdmin, isCliente])

  const canAccessWhatsApp = useCallback(() => {
    return isAdmin() || isCliente()
  }, [isAdmin, isCliente])

  const canAccessUsers = useCallback(() => {
    return isAdmin() || isCliente()
  }, [isAdmin, isCliente])

  const canCreateClients = useCallback(() => {
    return isAdmin()
  }, [isAdmin])

  // Função para verificar se o token está próximo de expirar
  const checkTokenExpiration = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return false
      
      // Decodificar o token JWT para verificar a expiração
      const payload = JSON.parse(atob(token.split('.')[1]))
      const expirationTime = payload.exp * 1000 // Converter para milissegundos
      const currentTime = Date.now()
      const timeUntilExpiration = expirationTime - currentTime
      
      // Se o token expira em menos de 5 minutos, renovar proativamente
      if (timeUntilExpiration < 5 * 60 * 1000) {
        console.log('🔄 Token expira em breve, renovando proativamente...')
        const newToken = await refreshToken()
        return !!newToken
      }
      
      return true
    } catch (error) {
      console.error('❌ Erro ao verificar expiração do token:', error)
      return false
    }
  }, [refreshToken])

  // Verificar token periodicamente
  useEffect(() => {
    const checkInterval = setInterval(() => {
      checkTokenExpiration()
    }, 5 * 60 * 1000) // Verificar a cada 5 minutos
    
    return () => clearInterval(checkInterval)
  }, [checkTokenExpiration])

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    refreshToken,
    checkTokenExpiration,
    updateProfile,
    changePassword,
    apiRequest,
    isAdmin,
    isCliente,
    isColaborador,
    canCreateUsers,
    canAccessReports,
    canAccessSettings,
    canAccessWhatsApp,
    canAccessUsers,
    canCreateClients,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}


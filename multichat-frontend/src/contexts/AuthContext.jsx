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
        logout()
        return null
      }

      const response = await fetch('http://localhost:8000/api/auth/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh }),
      })

      const data = await response.json()

      if (!response.ok) {
        logout()
        return null
      }

      localStorage.setItem('access_token', data.access)
      return data.access
    } catch (error) {
      console.error('Erro ao renovar token:', error)
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

  // OTIMIZADO: apiRequest com cache e timeout
  const apiRequest = useCallback(async (url, options = {}) => {
    let token = localStorage.getItem('access_token')
    
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
    const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 segundos

    try {
      let response = await fetch(fullUrl, {
        ...options,
        headers,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // Se o token expirou, tentar renovar
      if (response.status === 401) {
        const newToken = await refreshToken()
        
        if (newToken) {
          headers.Authorization = `Bearer ${newToken}`
          response = await fetch(fullUrl, {
            ...options,
            headers,
            signal: controller.signal,
          })
        }
      }

      return response
    } catch (error) {
      clearTimeout(timeoutId)
      if (error.name === 'AbortError') {
        throw new Error('Timeout na requisição')
      }
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

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    refreshToken,
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


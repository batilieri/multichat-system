import React, { createContext, useContext, useState, useEffect } from 'react'

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

  // Verificar se há token salvo no localStorage
  useEffect(() => {
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
      try {
        setUser(user)
        setIsAuthenticated(true)
        
        // Verificar se o token ainda é válido
        verifyToken(token)
      } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error)
        logout()
      }
    }
    
    setLoading(false)
  }, [])

  const verifyToken = async (token) => {
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
  }

  const login = async (email, password) => {
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
      return { success: false, error: error.message }
    }
  }

  // Função de logout corrigida
  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = "/login";
  };

  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token')
      
      if (!refresh) {
        throw new Error('Refresh token não encontrado')
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
        throw new Error('Erro ao renovar token')
      }

      localStorage.setItem('access_token', data.access)
      
      return data.access
    } catch (error) {
      console.error('Erro ao renovar token:', error)
      logout()
      return null
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('access_token')
      
      const response = await fetch('http://localhost:8000/api/auth/perfil/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Erro ao atualizar perfil')
      }

      // Atualizar dados do usuário
      const updatedUser = { ...user, ...data.usuario }
      setUser(updatedUser)
      localStorage.setItem('user_data', JSON.stringify(updatedUser))

      return { success: true, user: updatedUser }
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error)
      return { success: false, error: error.message }
    }
  }

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const token = localStorage.getItem('access_token')
      
      const response = await fetch('http://localhost:8000/api/auth/alterar-senha/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          senha_atual: currentPassword,
          nova_senha: newPassword,
          confirmar_nova_senha: newPassword,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Erro ao alterar senha')
      }

      return { success: true, message: data.message }
    } catch (error) {
      console.error('Erro ao alterar senha:', error)
      return { success: false, error: error.message }
    }
  }

  // Interceptor para requisições com token
  const apiRequest = async (url, options = {}) => {
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

    let response = await fetch(fullUrl, {
      ...options,
      headers,
    })

    // Se o token expirou, tentar renovar
    if (response.status === 401) {
      const newToken = await refreshToken()
      
      if (newToken) {
        headers.Authorization = `Bearer ${newToken}`
        response = await fetch(fullUrl, {
          ...options,
          headers,
        })
      }
    }

    return response
  }

  // Funções para verificar permissões
  const isAdmin = () => {
    console.log('🔍 Verificando isAdmin:', user);
    console.log('🔍 user.is_superuser:', user?.is_superuser);
    console.log('🔍 user.tipo_usuario:', user?.tipo_usuario);
    return user && (user.is_superuser || user.tipo_usuario === 'admin')
  }

  const isCliente = () => {
    return user && user.tipo_usuario === 'cliente'
  }

  const isColaborador = () => {
    return user && user.tipo_usuario === 'colaborador'
  }

  const canCreateUsers = () => {
    return isAdmin() || isCliente()
  }

  const canAccessReports = () => {
    return isAdmin() || isCliente()
  }

  const canAccessSettings = () => {
    return isAdmin() || isCliente()
  }

  const canAccessWhatsApp = () => {
    return isAdmin() || isCliente()
  }

  const canAccessUsers = () => {
    return isAdmin() || isCliente()
  }

  // Função para verificar se pode criar clientes (apenas admin)
  const canCreateClients = () => {
    return isAdmin()
  }

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


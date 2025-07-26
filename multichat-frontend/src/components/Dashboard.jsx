import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  MessageCircle,
  Users,
  Clock,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  PieChart,
  Calendar
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Pie
} from 'recharts'
import { useAuth } from '../contexts/AuthContext'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const { apiRequest } = useAuth()

  // Dados mock para desenvolvimento
  const mockStats = {
    total_chats: 156,
    chats_aguardando: 12,
    chats_em_andamento: 8,
    chats_resolvidos: 136,
    total_mensagens_hoje: 342,
    mensagens_recebidas_hoje: 198,
    mensagens_enviadas_hoje: 144,
    tempo_medio_resposta: 4.2,
    usuarios_ativos: 5,
    departamentos_ativos: 3,
    mensagens_por_dia: [
      { data: '2025-07-04', total: 245 },
      { data: '2025-07-05', total: 312 },
      { data: '2025-07-06', total: 189 },
      { data: '2025-07-07', total: 267 },
      { data: '2025-07-08', total: 298 },
      { data: '2025-07-09', total: 334 },
      { data: '2025-07-10', total: 342 }
    ],
    chats_por_status: {
      aguardando: 12,
      em_andamento: 8,
      resolvido: 136
    },
    mensagens_por_tipo: {
      text: 245,
      image: 67,
      document: 23,
      audio: 7
    },
    performance_usuarios: [
      { nome: 'João Silva', total_chats: 45, chats_resolvidos: 42, taxa_resolucao: 93.3 },
      { nome: 'Maria Santos', total_chats: 38, chats_resolvidos: 35, taxa_resolucao: 92.1 },
      { nome: 'Pedro Costa', total_chats: 32, chats_resolvidos: 28, taxa_resolucao: 87.5 }
    ]
  }

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Em desenvolvimento, usar dados mock
      // const response = await apiRequest('http://localhost:8000/api/dashboard/')
      // const data = await response.json()
      
      // Simular delay de carregamento
      setTimeout(() => {
        setStats(mockStats)
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error)
      setStats(mockStats)
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, change, icon: Icon, color = 'blue' }) => {
    const isPositive = change > 0
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.02 }}
        className="bg-card border border-border rounded-lg p-6 shadow-sm"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-muted-foreground text-sm font-medium">{title}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{value}</p>
            {change !== undefined && (
              <div className={`flex items-center mt-2 text-sm ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {isPositive ? (
                  <TrendingUp className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 mr-1" />
                )}
                <span>{Math.abs(change)}% vs ontem</span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-lg bg-${color}-100 dark:bg-${color}-900/20`}>
            <Icon className={`h-6 w-6 text-${color}-600 dark:text-${color}-400`} />
          </div>
        </div>
      </motion.div>
    )
  }

  const pieChartData = stats ? [
    { name: 'Aguardando', value: stats.chats_por_status.aguardando, color: '#f59e0b' },
    { name: 'Em Andamento', value: stats.chats_por_status.em_andamento, color: '#3b82f6' },
    { name: 'Resolvido', value: stats.chats_por_status.resolvido, color: '#10b981' }
  ] : []

  const messageTypeData = stats ? [
    { name: 'Texto', value: stats.mensagens_por_tipo.text },
    { name: 'Imagem', value: stats.mensagens_por_tipo.image },
    { name: 'Documento', value: stats.mensagens_por_tipo.document },
    { name: 'Áudio', value: stats.mensagens_por_tipo.audio }
  ] : []

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-lg p-6 animate-pulse">
              <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-muted rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-muted rounded w-1/3"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Visão geral do seu sistema de atendimento
            </p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Hoje, {new Date().toLocaleDateString('pt-BR')}</span>
          </div>
        </div>
      </div>

      {/* Conteúdo com scroll */}
      <div className="p-6 space-y-6 overflow-y-auto">
        {/* Cards de estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total de Chats"
            value={stats.total_chats}
            change={12}
            icon={MessageCircle}
            color="blue"
          />
          <StatCard
            title="Aguardando"
            value={stats.chats_aguardando}
            change={-5}
            icon={Clock}
            color="orange"
          />
          <StatCard
            title="Em Andamento"
            value={stats.chats_em_andamento}
            change={8}
            icon={Activity}
            color="blue"
          />
          <StatCard
            title="Resolvidos"
            value={stats.chats_resolvidos}
            change={15}
            icon={CheckCircle}
            color="green"
          />
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico de mensagens por dia */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-card border border-border rounded-lg p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Mensagens por Dia
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={stats.mensagens_por_dia}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="data" 
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#6b7280"
                  fontSize={12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Gráfico de status dos chats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-card border border-border rounded-lg p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Status dos Chats
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px'
                  }}
                />
              </RechartsPieChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Tabela de performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-card border border-border rounded-lg shadow-sm overflow-hidden"
        >
          <div className="p-6 border-b border-border">
            <h3 className="text-lg font-semibold text-foreground">
              Performance da Equipe
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Usuário
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Total de Chats
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Resolvidos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Taxa de Resolução
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {stats.performance_usuarios.map((user, index) => (
                  <tr key={index} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground">
                      {user.nome}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {user.total_chats}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {user.chats_resolvidos}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        user.taxa_resolucao >= 90 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                          : user.taxa_resolucao >= 80
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                      }`}>
                        {user.taxa_resolucao}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard


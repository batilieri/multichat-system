import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  MessageCircle,
  Clock,
  Download,
  Calendar,
  User,
  Filter,
  RefreshCw,
  Printer
} from 'lucide-react'
import {
  LineChart,
  Line,
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
  Pie,
  AreaChart,
  Area
} from 'recharts'
import { useAuth } from '../contexts/AuthContext'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Separator } from './ui/separator'

const Relatorios = () => {
  const [relatorio, setRelatorio] = useState(null)
  const [loading, setLoading] = useState(false)
  const [usuarios, setUsuarios] = useState([])
  const [filtros, setFiltros] = useState({
    data_inicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    data_fim: new Date().toISOString().split('T')[0],
    usuario_id: 'all',
    cliente_id: 'all'
  })
  const { apiRequest } = useAuth()

  // Dados mock para desenvolvimento
  const mockRelatorio = {
    periodo: {
      inicio: '2025-01-01',
      fim: '2025-01-31'
    },
    metricas: {
      atendimentos_periodo: 156,
      clientes_mes: 23,
      mensagens_enviadas_a_mais: 45,
      total_mensagens: 1247,
      tempo_medio_atendimento: 8.5,
      taxa_satisfacao: 87.3
    },
    graficos: {
      mensagens_por_dia: [
        { data: '2025-01-01', quantidade: 45 },
        { data: '2025-01-02', quantidade: 52 },
        { data: '2025-01-03', quantidade: 38 },
        { data: '2025-01-04', quantidade: 67 },
        { data: '2025-01-05', quantidade: 43 },
        { data: '2025-01-06', quantidade: 58 },
        { data: '2025-01-07', quantidade: 72 },
        { data: '2025-01-08', quantidade: 41 },
        { data: '2025-01-09', quantidade: 63 },
        { data: '2025-01-10', quantidade: 55 },
        { data: '2025-01-11', quantidade: 48 },
        { data: '2025-01-12', quantidade: 66 },
        { data: '2025-01-13', quantidade: 39 },
        { data: '2025-01-14', quantidade: 71 },
        { data: '2025-01-15', quantidade: 54 },
        { data: '2025-01-16', quantidade: 62 },
        { data: '2025-01-17', quantidade: 47 },
        { data: '2025-01-18', quantidade: 59 },
        { data: '2025-01-19', quantidade: 43 },
        { data: '2025-01-20', quantidade: 68 },
        { data: '2025-01-21', quantidade: 51 },
        { data: '2025-01-22', quantidade: 44 },
        { data: '2025-01-23', quantidade: 73 },
        { data: '2025-01-24', quantidade: 56 },
        { data: '2025-01-25', quantidade: 49 },
        { data: '2025-01-26', quantidade: 65 },
        { data: '2025-01-27', quantidade: 42 },
        { data: '2025-01-28', quantidade: 58 },
        { data: '2025-01-29', quantidade: 53 },
        { data: '2025-01-30', quantidade: 47 },
        { data: '2025-01-31', quantidade: 61 }
      ],
      atendimentos_por_status: [
        { status: 'aberto', total: 23 },
        { status: 'fechado', total: 98 },
        { status: 'pendente', total: 15 },
        { status: 'em_atendimento', total: 20 }
      ],
      top_atendentes: [
        { atendente__nome: 'João Silva', total_atendimentos: 45 },
        { atendente__nome: 'Maria Santos', total_atendimentos: 38 },
        { atendente__nome: 'Pedro Costa', total_atendimentos: 32 },
        { atendente__nome: 'Ana Oliveira', total_atendimentos: 28 },
        { atendente__nome: 'Carlos Lima', total_atendimentos: 25 }
      ],
      tipos_mensagem: [
        { tipo: 'texto', total: 856 },
        { tipo: 'imagem', total: 234 },
        { tipo: 'audio', total: 89 },
        { tipo: 'documento', total: 45 },
        { tipo: 'video', total: 23 }
      ]
    }
  }

  const mockUsuarios = [
    { id: 1, nome: 'João Silva', email: 'joao@empresa.com' },
    { id: 2, nome: 'Maria Santos', email: 'maria@empresa.com' },
    { id: 3, nome: 'Pedro Costa', email: 'pedro@empresa.com' },
    { id: 4, nome: 'Ana Oliveira', email: 'ana@empresa.com' },
    { id: 5, nome: 'Carlos Lima', email: 'carlos@empresa.com' }
  ]

  useEffect(() => {
    setUsuarios(mockUsuarios)
    carregarRelatorio()
  }, [])

  const carregarRelatorio = async () => {
    setLoading(true)
    try {
      // Em desenvolvimento, usar dados mock
      // Montar filtros sem 'all'
      const filtrosRequest = { ...filtros }
      if (filtrosRequest.usuario_id === 'all') delete filtrosRequest.usuario_id
      if (filtrosRequest.cliente_id === 'all') delete filtrosRequest.cliente_id
      
      // Simular delay de carregamento
      setTimeout(() => {
        setRelatorio(mockRelatorio)
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Erro ao carregar relatório:', error)
      setRelatorio(mockRelatorio)
      setLoading(false)
    }
  }

  const handleFiltroChange = (campo, valor) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor
    }))
  }

  const aplicarFiltros = () => {
    carregarRelatorio()
  }

  const imprimirRelatorio = () => {
    window.print()
  }

  const exportarRelatorio = () => {
    // Implementar exportação para PDF/Excel
    console.log('Exportando relatório...')
  }

  const formatarData = (data) => {
    return new Date(data).toLocaleDateString('pt-BR')
  }

  const formatarNumero = (numero) => {
    return numero.toLocaleString('pt-BR')
  }

  const coresGrafico = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  const MetricCard = ({ title, value, icon: Icon, color = 'blue', subtitle = '' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="bg-card border border-border rounded-lg p-6 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-muted-foreground text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-foreground mt-1">{formatarNumero(value)}</p>
          {subtitle && (
            <p className="text-muted-foreground text-xs mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-${color}-100 dark:bg-${color}-900/20`}>
          <Icon className={`h-6 w-6 text-${color}-600 dark:text-${color}-400`} />
        </div>
      </div>
    </motion.div>
  )

  if (loading || !relatorio) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          <span className="ml-4 text-muted-foreground text-lg">Carregando relatório...</span>
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
            <h1 className="text-3xl font-bold text-foreground">Relatórios</h1>
            <p className="text-muted-foreground mt-1">
              Análise detalhada do desempenho do sistema
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={imprimirRelatorio}>
              <Printer className="h-4 w-4 mr-2" />
              Imprimir
            </Button>
            <Button variant="outline" onClick={exportarRelatorio}>
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="p-6 border-b border-border bg-muted/30">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <Label htmlFor="data_inicio">Data Início</Label>
            <Input
              id="data_inicio"
              type="date"
              value={filtros.data_inicio}
              onChange={(e) => handleFiltroChange('data_inicio', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="data_fim">Data Fim</Label>
            <Input
              id="data_fim"
              type="date"
              value={filtros.data_fim}
              onChange={(e) => handleFiltroChange('data_fim', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="usuario">Usuário</Label>
            <Select value={filtros.usuario_id} onValueChange={(value) => handleFiltroChange('usuario_id', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Todos os usuários" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os usuários</SelectItem>
                {usuarios.map(usuario => (
                  <SelectItem key={usuario.id} value={usuario.id.toString()}>
                    {usuario.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="cliente">Cliente</Label>
            <Select value={filtros.cliente_id} onValueChange={(value) => handleFiltroChange('cliente_id', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Todos os clientes" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os clientes</SelectItem>
                <SelectItem value="1">Cliente A</SelectItem>
                <SelectItem value="2">Cliente B</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end">
            <Button onClick={aplicarFiltros} className="w-full">
              <Filter className="h-4 w-4 mr-2" />
              Aplicar Filtros
            </Button>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="p-6 space-y-6">
        {/* Período do relatório */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Período: {formatarData(relatorio.periodo.inicio)} a {formatarData(relatorio.periodo.fim)}
            </h2>
          </div>
          <Badge variant="secondary">
            {relatorio.graficos.mensagens_por_dia.length} dias analisados
          </Badge>
        </div>

        {/* Cards de métricas principais */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Atendimentos no Período"
            value={relatorio.metricas.atendimentos_periodo}
            icon={MessageCircle}
            color="blue"
            subtitle="Total de chats atendidos"
          />
          <MetricCard
            title="Clientes no Mês"
            value={relatorio.metricas.clientes_mes}
            icon={Users}
            color="green"
            subtitle="Novos clientes cadastrados"
          />
          <MetricCard
            title="Mensagens a Mais"
            value={relatorio.metricas.mensagens_enviadas_a_mais}
            icon={TrendingUp}
            color="orange"
            subtitle="Comparado ao período anterior"
          />
          <MetricCard
            title="Total de Mensagens"
            value={relatorio.metricas.total_mensagens}
            icon={BarChart3}
            color="purple"
            subtitle="Mensagens no período"
          />
        </div>

        {/* Métricas adicionais */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard
            title="Tempo Médio de Atendimento"
            value={`${relatorio.metricas.tempo_medio_atendimento} min`}
            icon={Clock}
            color="indigo"
            subtitle="Tempo médio por chat"
          />
          <MetricCard
            title="Taxa de Satisfação"
            value={`${relatorio.metricas.taxa_satisfacao}%`}
            icon={TrendingUp}
            color="emerald"
            subtitle="Baseado em feedback positivo"
          />
        </div>

        <Separator />

        {/* Gráficos */}
        <div className="space-y-6">
          {/* Gráfico de mensagens por dia */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Mensagens por Dia
              </CardTitle>
              <CardDescription>
                Evolução do volume de mensagens ao longo do período
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={relatorio.graficos.mensagens_por_dia}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="data" 
                    tickFormatter={(value) => formatarData(value)}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => formatarData(value)}
                    formatter={(value) => [formatarNumero(value), 'Mensagens']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="quantidade" 
                    stroke="#3b82f6" 
                    fill="#3b82f6" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de atendimentos por status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <PieChart className="h-5 w-5 mr-2" />
                  Atendimentos por Status
                </CardTitle>
                <CardDescription>
                  Distribuição dos chats por status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={relatorio.graficos.atendimentos_por_status}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="total"
                    >
                      {relatorio.graficos.atendimentos_por_status.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={coresGrafico[index % coresGrafico.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [formatarNumero(value), 'Atendimentos']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Gráfico de tipos de mensagem */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Tipos de Mensagem
                </CardTitle>
                <CardDescription>
                  Distribuição por tipo de conteúdo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={relatorio.graficos.tipos_mensagem}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="tipo" />
                    <YAxis />
                    <Tooltip formatter={(value) => [formatarNumero(value), 'Mensagens']} />
                    <Bar dataKey="total" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Top atendentes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Top 5 Atendentes Mais Ativos
              </CardTitle>
              <CardDescription>
                Ranking dos atendentes com mais atendimentos no período
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={relatorio.graficos.top_atendentes} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="atendente__nome" type="category" width={120} />
                  <Tooltip formatter={(value) => [formatarNumero(value), 'Atendimentos']} />
                  <Bar dataKey="total_atendimentos" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Relatorios 
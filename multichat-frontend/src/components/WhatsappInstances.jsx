import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { toast } from "../components/ui/use-toast";
import { Smartphone, Wifi, WifiOff, QrCode, RefreshCw, Send, Plus, Settings, Trash } from 'lucide-react';
import axios from 'axios';
import { getInstanceStatus, getInstanceQRCode, saveInstanceLocally, getTokenForInstance } from '../lib/wapi';
import { useAuth } from '../contexts/AuthContext';

// Componente otimizado para o badge de status
const StatusBadge = React.memo(({ status }) => {
  switch (status) {
    case 'conectado':
    case 'connected':
      return <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200"><Wifi className="w-3 h-3 mr-1" />Conectado</Badge>;
    case 'desconectado':
    case 'disconnected':
      return <Badge variant="outline" className="bg-red-100 text-red-800 border-red-200"><WifiOff className="w-3 h-3 mr-1" />Desconectado</Badge>;
    case 'qrcode_gerado':
      return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-200"><QrCode className="w-3 h-3 mr-1" />QR Code</Badge>;
    case 'pendente':
      return <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-200"><RefreshCw className="w-3 h-3 mr-1" />Pendente</Badge>;
    default:
      return <Badge variant="outline" className="bg-gray-100 text-gray-800 border-gray-200">Desconhecido</Badge>;
  }
});

StatusBadge.displayName = 'StatusBadge';

/**
 * Componente para gerenciamento de instâncias do WhatsApp via W-APi.
 *
 * Permite:
 * - Visualizar todas as instâncias conectadas
 * - Conectar novas instâncias a clientes
 * - Verificar status de conexão
 * - Gerar QR Codes
 * - Enviar mensagens de teste
 * - Gerenciar configurações de webhook
 */
function WhatsappInstances() {
  const { isAdmin, isCliente, isColaborador } = useAuth();
  const [instances, setInstances] = useState([]);
  const [clients, setClients] = useState([]);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [isQrModalOpen, setIsQrModalOpen] = useState(false);
  const [isSendMessageModalOpen, setIsSendMessageModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState('');
  const [instanceId, setInstanceId] = useState('');
  const [token, setToken] = useState('');
  const [webhookUrl, setWebhookUrl] = useState('https://167.86.75.207/webhook');
  const [qrCodeData, setQrCodeData] = useState('');
  const [selectedInstance, setSelectedInstance] = useState(null);
  const [editingInstance, setEditingInstance] = useState(null);
  const [testMessage, setTestMessage] = useState('');
  const [testPhoneNumber, setTestPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  // Novo estado para status detalhado e loading de status
  const [instanceStatus, setInstanceStatus] = useState({}); // { [instanceId]: { status, ... } }
  const [statusLoading, setStatusLoading] = useState({}); // { [instanceId]: boolean }
  const [qrLoading, setQrLoading] = useState(false);
  const [qrError, setQrError] = useState('');

  // [1] Adicionar estados para modal de edição e remoção
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [deletingInstance, setDeletingInstance] = useState(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  /**
   * Busca todas as instâncias do WhatsApp.
   */
  const fetchInstances = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('Token de acesso não encontrado');
        toast({
          title: "Erro de Autenticação",
          description: "Token de acesso não encontrado. Faça login novamente.",
          variant: "destructive",
        });
        setInstances([]);
        return;
      }

      console.log('Buscando instâncias...');
      const response = await axios.get(`${API_BASE_URL}/api/whatsapp-instances/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        timeout: 10000, // 10 segundos de timeout
      });
      
      console.log('Resposta da API de instâncias:', response.data);
      
      // Lidar com resposta paginada
      const data = response.data.results || response.data;
      const instancesArray = Array.isArray(data) ? data : [];
      
      console.log(`Instâncias encontradas: ${instancesArray.length}`);
      setInstances(instancesArray);
      
      // Inicializar status baseado no status do banco de dados
      const initialStatus = {};
      instancesArray.forEach(instance => {
        if (instance.status) {
          initialStatus[instance.instance_id] = {
            status: instance.status,
            message: `Status inicial: ${instance.status}`,
            instance_id: instance.instance_id
          };
        }
      });
      
      if (Object.keys(initialStatus).length > 0) {
        console.log('📊 Inicializando status baseado no banco:', initialStatus);
        setInstanceStatus(initialStatus);
      }
      
      // Se não há instâncias, mostrar mensagem informativa
      if (instancesArray.length === 0) {
        toast({
          title: "Informação",
          description: "Nenhuma instância WhatsApp encontrada. Conecte uma nova instância.",
        });
      }
      
    } catch (error) {
      console.error('Erro ao buscar instâncias:', error);
      console.error('Detalhes do erro:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        config: error.config
      });
      
      setInstances([]);
      
      let errorMessage = "Falha ao carregar instâncias do WhatsApp.";
      
      if (error.response?.status === 401) {
        errorMessage = "Sessão expirada. Faça login novamente.";
      } else if (error.response?.status === 403) {
        errorMessage = "Sem permissão para acessar instâncias.";
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = "Timeout na conexão com o servidor.";
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage = "Erro de rede. Verifique sua conexão.";
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  /**
   * Busca todos os clientes disponíveis.
   */
  const fetchClients = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE_URL}/api/clientes/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      console.log('Resposta da API de clientes:', response.data);
      // Ajuste para aceitar diferentes formatos de resposta
      let data = response.data;
      if (Array.isArray(data)) {
        setClients(data);
      } else if (Array.isArray(data.results)) {
        setClients(data.results);
      } else if (Array.isArray(data.clientes)) {
        setClients(data.clientes);
      } else {
        setClients([]);
      }
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      setClients([]);
      toast({
        title: "Erro",
        description: "Falha ao carregar clientes.",
        variant: "destructive",
      });
    }
  };

  // Função para salvar instância/token localmente e já verificar status
  const handleConnectInstance = async () => {
    if (!selectedClient || !instanceId || !token) {
      toast({
        title: "Erro",
        description: "Todos os campos são obrigatórios.",
        variant: "destructive",
      });
      return;
    }
    setLoading(true);
    try {
      // Salva localmente para uso futuro
      saveInstanceLocally(instanceId, token);
      
      // Salvar no backend
      const authToken = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE_URL}/api/clientes/${selectedClient}/connect_wapi/`,
        {
          instance_id: instanceId,
          token: token,
          webhook_url: webhookUrl,
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );

      toast({
        title: "Sucesso",
        description: "Instância W-APi conectada com sucesso!",
      });

      // Após salvar, já verifica status na W-API
      await checkAndSetInstanceStatus(instanceId);
      
      // Limpar formulário e fechar modal
      setSelectedClient('');
      setInstanceId('');
      setToken('');
      setWebhookUrl('https://167.86.75.207/webhook');
      setIsConnectModalOpen(false);
      
      // Recarregar instâncias
      fetchInstances();
    } catch (error) {
      console.error('Erro ao conectar instância:', error);
      toast({
        title: "Erro",
        description: error.response?.data?.error || error.message || "Falha ao conectar instância.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Função para verificar status de uma instância usando o endpoint correto
  const checkAndSetInstanceStatus = async (instanceId) => {
    console.log(`🔄 Verificando status da instância: ${instanceId}`);
    setStatusLoading((prev) => ({ ...prev, [instanceId]: true }));
    try {
      // Buscar a instância no array local para obter o token
      const instance = instances.find(inst => inst.instance_id === instanceId);
      if (!instance) {
        console.warn(`Instância ${instanceId} não encontrada no array local`);
        return;
      }
      
      // Usar o endpoint correto da API do backend que faz proxy para WAPI
      const authToken = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/wapi/auth/status/`,
        {
          params: { instanceId },
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      
      console.log(`✅ Status da instância ${instanceId}:`, response.data);
      
      // Manter o status anterior se a nova resposta não tiver status
      setInstanceStatus((prev) => {
        const currentStatus = prev[instanceId] || {};
        const newStatus = response.data || {};
        
        // Se a nova resposta não tem status, manter o anterior
        if (!newStatus.status && currentStatus.status) {
          console.log(`⚠️ Mantendo status anterior para ${instanceId}: ${currentStatus.status}`);
          return prev;
        }
        
        // Só atualizar se o status realmente mudou
        if (currentStatus.status === newStatus.status) {
          console.log(`✅ Status inalterado para ${instanceId}: ${newStatus.status}`);
          return prev;
        }
        
        console.log(`📊 Atualizando status de ${instanceId}: ${currentStatus.status} → ${newStatus.status}`);
        return { ...prev, [instanceId]: newStatus };
      });
    } catch (error) {
      console.error(`❌ Erro ao verificar status da instância ${instanceId}:`, error);
      
      // Não sobrescrever status válido com erro
      setInstanceStatus((prev) => {
        const currentStatus = prev[instanceId];
        if (currentStatus && currentStatus.status && currentStatus.status !== 'erro') {
          console.log(`⚠️ Mantendo status válido para ${instanceId}: ${currentStatus.status}`);
          return prev;
        }
        
        return { 
          ...prev, 
          [instanceId]: { 
            status: 'erro', 
            error: error.response?.data?.error || error.message 
          } 
        };
      });
    } finally {
      setStatusLoading((prev) => ({ ...prev, [instanceId]: false }));
    }
  };

  // Chamar checkAndSetInstanceStatus para cada instância ao carregar/fetchInstances
  useEffect(() => {
    instances.forEach((inst) => {
      checkAndSetInstanceStatus(inst.instance_id);
    });
    // eslint-disable-next-line
  }, [instances.length]);

  // Polling automático para atualizar status das instâncias a cada 10 segundos usando handleRefreshStatus
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('🔄 Polling automático - handleRefreshStatus para todas as instâncias (silent)...');
      instances.forEach((inst) => {
        handleRefreshStatus(inst.id, true);
      });
    }, 10000); // 10 segundos
    return () => clearInterval(interval);
  }, [instances]);

  // Função para carregar tokens do backend para localStorage
  const loadTokensFromBackend = async () => {
    try {
      const authToken = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/whatsapp-instances/`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      
      // Para cada instância, buscar dados completos incluindo token
      for (const instance of response.data.results || []) {
        try {
          const instanceResponse = await axios.get(
            `${API_BASE_URL}/api/whatsapp-instances/${instance.id}/get_for_edit/`,
            {
              headers: {
                Authorization: `Bearer ${authToken}`,
              },
            }
          );
          
          // Salvar token no localStorage
          if (instanceResponse.data.token) {
            saveInstanceLocally(instanceResponse.data.instance_id, instanceResponse.data.token);
          }
        } catch (error) {
          console.warn(`Erro ao carregar token para instância ${instance.instance_id}:`, error);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar tokens do backend:', error);
    }
  };

  // useEffect para carregar dados iniciais (instâncias e clientes)
  useEffect(() => {
    fetchInstances();
    fetchClients();
    loadTokensFromBackend(); // Carregar tokens do backend
  }, []);

  // Função para abrir modal de QR Code e buscar QR Code da W-API
  const handleOpenQrModal = async (instance) => {
    setSelectedInstance(instance);
    setQrCodeData('');
    setQrError('');
    setIsQrModalOpen(true);
    setQrLoading(true);
    try {
      // Usar o endpoint correto do backend que faz proxy para WAPI
      const authToken = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/wapi/auth/qrcode/`,
        {
          params: { instanceId: instance.instance_id },
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      
      // Extrair QR Code da resposta
      const qrCode = response.data.qr_code || response.data.qrCode || response.data.qrcode || '';
      setQrCodeData(qrCode);
      
      if (!qrCode) {
        setQrError('QR Code não disponível. Verifique se a instância está configurada corretamente.');
      }
    } catch (error) {
      console.error('Erro ao buscar QR Code:', error);
      setQrError(error.response?.data?.error || error.message || 'Erro ao buscar QR Code');
    } finally {
      setQrLoading(false);
    }
  };

  // Função para revalidar status após escanear QR
  const handleRevalidateStatus = async () => {
    if (!selectedInstance) return;
    
    setQrLoading(true);
    try {
      // Verificar status usando o endpoint correto
      await checkAndSetInstanceStatus(selectedInstance.instance_id);
      
      // Aguardar um pouco e verificar novamente para dar tempo da conexão
      setTimeout(async () => {
        await checkAndSetInstanceStatus(selectedInstance.instance_id);
        fetchInstances();
      }, 2000);
      
      toast({
        title: "Status Verificado",
        description: "Status da instância atualizado. Verifique se está conectado.",
      });
    } catch (error) {
      console.error('Erro ao revalidar status:', error);
      toast({
        title: "Erro",
        description: "Erro ao verificar status da instância.",
        variant: "destructive",
      });
    } finally {
      setQrLoading(false);
    }
  };

  // Função para testar conexão da instância
  const handleTestConnection = async () => {
    if (!selectedInstance) return;
    
    setQrLoading(true);
    try {
      const authToken = localStorage.getItem('access_token');
      
      // Testar conexão usando o endpoint de status da WAPI
      const response = await axios.get(
        `${API_BASE_URL}/api/wapi/auth/status/`,
        {
          params: { instanceId: selectedInstance.instance_id },
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      
      const statusData = response.data;
      console.log('📊 Resultado do teste de conexão:', statusData);
      
      // Atualizar status local
      setInstanceStatus(prev => ({
        ...prev,
        [selectedInstance.instance_id]: {
          status: statusData.status || statusData.connectionStatus || 'desconhecido',
          message: statusData.message || statusData.status || 'Status verificado',
          instance_id: selectedInstance.instance_id,
          lastChecked: new Date().toISOString()
        }
      }));
      
      // Verificar se está conectado
      const isConnected = statusData.status === 'connected' || 
                         statusData.status === 'conectado' || 
                         statusData.connectionStatus === 'connected' ||
                         statusData.connectionStatus === 'conectado';
      
      if (isConnected) {
        toast({
          title: "✅ Conexão Testada",
          description: "Instância está conectada e funcionando corretamente!",
        });
        
        // Atualizar lista de instâncias para refletir o novo status
        fetchInstances();
      } else {
        toast({
          title: "⚠️ Status da Conexão",
          description: `Instância não está conectada. Status: ${statusData.status || statusData.connectionStatus || 'desconhecido'}`,
          variant: "destructive",
        });
      }
      
    } catch (error) {
      console.error('Erro ao testar conexão:', error);
      
      let errorMessage = "Erro ao testar conexão da instância.";
      
      if (error.response?.status === 404) {
        errorMessage = "Instância não encontrada ou endpoint inválido.";
      } else if (error.response?.status === 401) {
        errorMessage = "Token de autenticação inválido.";
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      }
      
      toast({
        title: "❌ Erro no Teste",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setQrLoading(false);
    }
  };

  /**
   * Atualiza o status de uma instância específica.
   */
  const handleRefreshStatus = async (instanceId, silent = false) => {
    setLoading(true);
    try {
      const authToken = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE_URL}/api/whatsapp-instances/${instanceId}/refresh_status/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );

      if (!silent) {
        toast({
          title: "Sucesso",
          description: "Status atualizado com sucesso!",
        });
      }

      fetchInstances();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      if (!silent) {
        toast({
          title: "Erro",
          description: "Falha ao atualizar status da instância.",
          variant: "destructive",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Gera um novo QR Code para uma instância.
   */
  const handleGenerateQR = async (instanceId) => {
    setLoading(true);
    try {
      const authToken = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/whatsapp-instances/${instanceId}/generate_qr/`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );

      setQrCodeData(response.data.qr_code);
      setIsQrModalOpen(true);

      toast({
        title: "Sucesso",
        description: "QR Code gerado com sucesso!",
      });
    } catch (error) {
      console.error('Erro ao gerar QR Code:', error);
      toast({
        title: "Erro",
        description: "Falha ao gerar QR Code.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Envia uma mensagem de teste através de uma instância.
   */
  const handleSendTestMessage = async () => {
    if (!testPhoneNumber || !testMessage) {
      toast({
        title: "Erro",
        description: "Número e mensagem são obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const authToken = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE_URL}/api/whatsapp-instances/${selectedInstance.id}/send_message/`,
        {
          numero_destino: testPhoneNumber,
          mensagem: testMessage,
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );

      toast({
        title: "Sucesso",
        description: "Mensagem enviada com sucesso!",
      });

      setTestPhoneNumber('');
      setTestMessage('');
      setIsSendMessageModalOpen(false);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      toast({
        title: "Erro",
        description: error.response?.data?.error || "Falha ao enviar mensagem.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Retorna o ícone e cor apropriados para o status da instância.
   */
  const getStatusBadge = (status) => {
    switch (status) {
      case 'conectado':
      case 'connected':
        return <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200"><Wifi className="w-3 h-3 mr-1" />Conectado</Badge>;
      case 'desconectado':
      case 'disconnected':
        return <Badge variant="outline" className="bg-red-100 text-red-800 border-red-200"><WifiOff className="w-3 h-3 mr-1" />Desconectado</Badge>;
      case 'qrcode_gerado':
        return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-200"><QrCode className="w-3 h-3 mr-1" />QR Code</Badge>;
      case 'pendente':
        return <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-200"><RefreshCw className="w-3 h-3 mr-1" />Pendente</Badge>;
      default:
        return <Badge variant="outline" className="bg-gray-100 text-gray-800 border-gray-200">Desconhecido</Badge>;
    }
  };

  /**
   * Abre o modal para enviar mensagem de teste.
   */
  const openSendMessageModal = (instance) => {
    setSelectedInstance(instance);
    setIsSendMessageModalOpen(true);
  };

  // [2] Função para abrir modal de edição
  const openEditModal = async (instance) => {
    try {
      const authToken = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/whatsapp-instances/${instance.id}/get_for_edit/`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      setEditingInstance(response.data);
      setIsEditModalOpen(true);
    } catch (error) {
      console.error('Erro ao buscar dados da instância:', error);
      toast({
        title: "Erro",
        description: "Falha ao carregar dados da instância para edição.",
        variant: "destructive",
      });
    }
  };

  // [3] Função para abrir modal de confirmação de remoção
  const openDeleteConfirm = (instance) => {
    setDeletingInstance(instance);
    setIsDeleteConfirmOpen(true);
  };

  // [4] Função para editar instância
  const handleEditInstance = async () => {
    if (!editingInstance.instance_id || !editingInstance.token) {
      toast({
        title: "Erro",
        description: "ID da instância e token são obrigatórios.",
        variant: "destructive",
      });
      return;
    }
    setLoading(true);
    try {
      const authToken = localStorage.getItem('access_token');
      await axios.put(
        `${API_BASE_URL}/api/whatsapp-instances/${editingInstance.id}/`,
        {
          instance_id: editingInstance.instance_id,
          token: editingInstance.token,
          status: editingInstance.status,
          qr_code: editingInstance.qr_code,
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      // Salvar token localmente também
      saveInstanceLocally(editingInstance.instance_id, editingInstance.token);
      
      toast({
        title: "Sucesso",
        description: "Instância editada com sucesso!",
      });
      setIsEditModalOpen(false);
      setEditingInstance(null);
      fetchInstances();
    } catch (error) {
      toast({
        title: "Erro",
        description: error.response?.data?.error || "Falha ao editar instância.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Adicione a função abaixo dentro do componente WhatsappInstances
  const handleDisconnectInstance = async () => {
    if (!editingInstance?.instance_id) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE_URL}/api/wapi/auth/disconnect/?instanceId=${editingInstance.instance_id}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      toast({
        title: 'Desconectado',
        description: response.data.message || 'Instância desconectada com sucesso!',
      });
      fetchInstances();
      setIsEditModalOpen(false);
    } catch (error) {
      toast({
        title: 'Erro ao desconectar',
        description: error.response?.data?.error || 'Falha ao desconectar instância.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // [5] Função para remover instância
  const handleDeleteInstance = async () => {
    setLoading(true);
    try {
      const authToken = localStorage.getItem('access_token');
      await axios.delete(
        `${API_BASE_URL}/api/whatsapp-instances/${deletingInstance.id}/`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      toast({
        title: "Sucesso",
        description: "Instância removida com sucesso!",
      });
      setIsDeleteConfirmOpen(false);
      setDeletingInstance(null);
      fetchInstances();
    } catch (error) {
      toast({
        title: "Erro",
        description: error.response?.data?.error || "Falha ao remover instância.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Função para abrir modal para conectar nova instância.
  const openConnectModal = () => {
    // Limpar campos ao abrir o modal
    setSelectedClient('');
    setInstanceId('');
    setToken('');
    setWebhookUrl('https://167.86.75.207/webhook');
    setIsConnectModalOpen(true);
  };

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Instâncias WhatsApp</h1>
            <p className="text-muted-foreground">
              {isAdmin() ? 'Gerencie suas conexões WhatsApp' : 'Visualize suas conexões WhatsApp'}
            </p>
          </div>
          {isAdmin() && (
            <Button onClick={openConnectModal} className="flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span>Conectar Instância</span>
            </Button>
          )}
        </div>
      </div>

      {/* Conteúdo com scroll */}
      <div className="p-6 space-y-6 overflow-y-auto">
        {/* Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-2xl font-bold">{instances.length}</p>
                </div>
                <Smartphone className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Conectadas</p>
                  <p className="text-2xl font-bold text-green-600">
                    {instances.filter(i => instanceStatus[i.instance_id]?.status === 'conectado').length}
                  </p>
                </div>
                <Wifi className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Desconectadas</p>
                  <p className="text-2xl font-bold text-red-600">
                    {instances.filter(i => instanceStatus[i.instance_id]?.status === 'desconectado').length}
                  </p>
                </div>
                <WifiOff className="w-8 h-8 text-red-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Aguardando QR</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {instances.filter(i => instanceStatus[i.instance_id]?.status === 'qrcode_gerado').length}
                  </p>
                </div>
                <QrCode className="w-8 h-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabela de Instâncias */}
        <Card>
          <CardHeader>
            <CardTitle>Instâncias Conectadas</CardTitle>
            <CardDescription>
              Lista de todas as instâncias do WhatsApp conectadas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID da Instância</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Última Conexão</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {instances.map((instance) => (
                  <TableRow key={instance.id}>
                    <TableCell className="font-mono">{instance.instance_id}</TableCell>
                    <TableCell>{instance.cliente_nome || 'Não atribuído'}</TableCell>
                    <TableCell><StatusBadge status={instanceStatus[instance.instance_id]?.status || instance.status} /></TableCell>
                    <TableCell>
                      {instanceStatus[instance.instance_id]?.last_seen 
                        ? new Date(instanceStatus[instance.instance_id]?.last_seen).toLocaleString('pt-BR')
                        : 'Nunca'
                      }
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRefreshStatus(instance.id)}
                          disabled={loading}
                        >
                          <RefreshCw className="w-3 h-3" />
                        </Button>
                        {/* Botão de QR Code sempre visível para testes */}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleOpenQrModal(instance)}
                          disabled={qrLoading}
                        >
                          <QrCode className="w-3 h-3" />
                        </Button>
                        {instanceStatus[instance.instance_id]?.status === 'conectado' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openSendMessageModal(instance)}
                          >
                            <Send className="w-3 h-3" />
                          </Button>
                        )}
                        {isAdmin() && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openEditModal(instance)}
                              disabled={loading}
                            >
                              <Settings className="w-3 h-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => openDeleteConfirm(instance)}
                              disabled={loading}
                              title="Remover"
                            >
                              <Trash className="w-4 h-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Modal: Conectar Nova Instância */}
      {isAdmin() && (
        <Dialog open={isConnectModalOpen} onOpenChange={setIsConnectModalOpen}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Conectar Nova Instância WhatsApp</DialogTitle>
              <DialogDescription>
                Conecte uma nova instância do WhatsApp a um cliente específico.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="client">Cliente</Label>
                <Select value={selectedClient} onValueChange={setSelectedClient}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map((client) => (
                      client.id ? (
                        <SelectItem key={client.id} value={client.id.toString()}>
                          {/* Busca o campo de nome mais adequado */}
                          {client.nome || client.name || client.razao_social || client.empresa || `Cliente #${client.id}`}
                        </SelectItem>
                      ) : null
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="instanceId">ID da Instância</Label>
                <Input
                  id="instanceId"
                  placeholder="Ex: 3B6XIW-ZTS923-GEAY6V"
                  value={instanceId}
                  onChange={(e) => setInstanceId(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="token">Token</Label>
                <Input
                  id="token"
                  type="password"
                  placeholder="Ex: Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="webhookUrl">URL do Webhook</Label>
                <Input
                  id="webhookUrl"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsConnectModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleConnectInstance} disabled={loading}>
                {loading ? 'Conectando...' : 'Conectar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Modal: QR Code */}
      <Dialog open={isQrModalOpen} onOpenChange={setIsQrModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>QR Code para Conexão - {selectedInstance?.instance_id}</DialogTitle>
            <DialogDescription>
              Escaneie este QR Code com o WhatsApp para conectar a instância.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Status atual da instância */}
            <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Status Atual:</span>
                <div className="flex items-center gap-2">
                  {instanceStatus[selectedInstance?.instance_id] ? (
                    <>
                      {selectedInstance && <StatusBadge status={instanceStatus[selectedInstance?.instance_id].status} />}
                      <span className="text-xs text-gray-500">
                        {instanceStatus[selectedInstance?.instance_id].lastChecked && 
                          new Date(instanceStatus[selectedInstance?.instance_id].lastChecked).toLocaleTimeString()}
                      </span>
                    </>
                  ) : (
                    <Badge className="bg-gray-100 text-gray-800">Não verificado</Badge>
                  )}
                </div>
              </div>
            </div>

            {/* QR Code */}
            <div className="flex justify-center p-4">
              {qrLoading ? (
                <div className="flex flex-col items-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="text-sm text-gray-600">Carregando QR Code...</p>
                </div>
              ) : qrCodeData ? (
                <div className="text-center">
                  <img 
                    src={qrCodeData} 
                    alt="QR Code" 
                    className="max-w-full h-auto border rounded shadow-lg"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Escaneie com o WhatsApp para conectar
                  </p>
                </div>
              ) : qrError ? (
                <div className="text-center">
                  <p className="text-red-500 text-sm">{qrError}</p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleOpenQrModal.bind(null, selectedInstance)}
                    className="mt-2"
                  >
                    Tentar Novamente
                  </Button>
                </div>
              ) : (
                <p className="text-gray-500">QR Code não disponível</p>
              )}
            </div>

            {/* Instruções */}
            <div className="bg-blue-50 dark:bg-blue-950/20 p-3 rounded-lg">
              <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
                📱 Como conectar:
              </h4>
              <ol className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                <li>1. Abra o WhatsApp no seu celular</li>
                <li>2. Vá em Configurações → Dispositivos Vinculados</li>
                <li>3. Toque em "Vincular um Dispositivo"</li>
                <li>4. Escaneie o QR Code acima</li>
                <li>5. Use o botão "Testar Conexão" para verificar</li>
              </ol>
            </div>
          </div>

          <DialogFooter className="flex flex-col sm:flex-row gap-2">
            <Button 
              variant="outline" 
              onClick={() => setIsQrModalOpen(false)}
              className="w-full sm:w-auto"
            >
              Fechar
            </Button>
            <Button 
              onClick={handleTestConnection} 
              disabled={qrLoading}
              className="w-full sm:w-auto bg-green-600 hover:bg-green-700"
            >
              {qrLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Testando...
                </>
              ) : (
                <>
                  <Wifi className="w-4 h-4 mr-2" />
                  Testar Conexão
                </>
              )}
            </Button>
            <Button 
              onClick={handleRevalidateStatus} 
              disabled={qrLoading}
              variant="secondary"
              className="w-full sm:w-auto"
            >
              {qrLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Verificando...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Verificar Status
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal: Enviar Mensagem de Teste */}
      <Dialog open={isSendMessageModalOpen} onOpenChange={setIsSendMessageModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Enviar Mensagem de Teste</DialogTitle>
            <DialogDescription>
              Envie uma mensagem de teste através da instância {selectedInstance?.instance_id}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="phoneNumber">Número do Destinatário</Label>
              <Input
                id="phoneNumber"
                placeholder="Ex: 5511999999999"
                value={testPhoneNumber}
                onChange={(e) => setTestPhoneNumber(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="message">Mensagem</Label>
              <Input
                id="message"
                placeholder="Digite sua mensagem de teste"
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsSendMessageModalOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSendTestMessage} disabled={loading}>
              {loading ? 'Enviando...' : 'Enviar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de edição de instância */}
      {isAdmin() && (
        <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Editar Instância WhatsApp</DialogTitle>
              <DialogDescription>
                Edite os dados da instância do WhatsApp.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit_instance_id">ID da Instância</Label>
                <Input
                  id="edit_instance_id"
                  value={editingInstance?.instance_id || ''}
                  onChange={(e) => setEditingInstance(prev => ({ ...prev, instance_id: e.target.value }))}
                  placeholder="ID da instância"
                />
              </div>
              <div>
                <Label htmlFor="edit_token">Token</Label>
                <Input
                  id="edit_token"
                  type="password"
                  value={editingInstance?.token || ''}
                  onChange={(e) => setEditingInstance(prev => ({ ...prev, token: e.target.value }))}
                  placeholder="Token da instância"
                />
              </div>
              <div>
                <Label htmlFor="edit_status">Status</Label>
                <Select
                  value={editingInstance?.status || 'pendente'}
                  onValueChange={(value) => setEditingInstance(prev => ({ ...prev, status: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pendente">Pendente</SelectItem>
                    <SelectItem value="conectado">Conectado</SelectItem>
                    <SelectItem value="desconectado">Desconectado</SelectItem>
                    <SelectItem value="qrcode_gerado">QR Code Gerado</SelectItem>
                    <SelectItem value="erro">Erro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleEditInstance} disabled={loading}>
                {loading ? 'Salvando...' : 'Salvar'}
              </Button>
              <Button variant="destructive" onClick={handleDisconnectInstance} disabled={loading}>
                {loading ? 'Desconectando...' : 'Desconectar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Modal de confirmação de remoção */}
      {isAdmin() && (
        <Dialog open={isDeleteConfirmOpen} onOpenChange={setIsDeleteConfirmOpen}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Remover Instância</DialogTitle>
              <DialogDescription>Tem certeza que deseja remover esta instância? Esta ação não pode ser desfeita.</DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDeleteConfirmOpen(false)}>
                Cancelar
              </Button>
              <Button variant="destructive" onClick={handleDeleteInstance} disabled={loading}>
                {loading ? 'Removendo...' : 'Remover'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

export default WhatsappInstances;


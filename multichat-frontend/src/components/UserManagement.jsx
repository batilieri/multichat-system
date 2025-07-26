import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "../components/ui/use-toast";
import { useIsMobile } from "../hooks/use-mobile";
import { useAuth } from "../contexts/AuthContext";
import axios from 'axios';
import { Pencil, Trash } from 'lucide-react';
import { Badge } from "../components/ui/badge";
import { getInstanceStatus, getTokenForInstance } from '../lib/wapi';
import { Wifi, WifiOff } from 'lucide-react';

/**
 * Componente para gerenciamento de usuários e clientes.
 *
 * Permite visualizar, adicionar, editar e excluir usuários e clientes.
 * Inclui a funcionalidade de conectar clientes a instâncias do W-APi.
 * Responsivo para dispositivos móveis com paginação adaptativa.
 */
function UserManagement() {
  const { isAdmin, isCliente, isColaborador, canCreateClients } = useAuth();
  
  // Debug: Log das permissões do usuário
  console.log('🔍 UserManagement - Debug de permissões:');
  console.log('   isAdmin():', isAdmin());
  console.log('   isCliente():', isCliente());
  console.log('   isColaborador():', isColaborador());
  console.log('   canCreateClients():', canCreateClients());
  
  const [users, setUsers] = useState([]);
  const [clients, setClients] = useState([]);
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [isClientModalOpen, setIsClientModalOpen] = useState(false);
  const [isConnectWapiModalOpen, setIsConnectWapiModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [editingClient, setEditingClient] = useState(null);
  const [selectedClientForWapi, setSelectedClientForWapi] = useState(null);
  const [wapiInstanceId, setWapiInstanceId] = useState('');
  const [wapiToken, setWapiToken] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Estados para paginação móvel
  const [currentUserPage, setCurrentUserPage] = useState(0);
  const [currentClientPage, setCurrentClientPage] = useState(0);
  const [activeTab, setActiveTab] = useState('users'); // 'users' ou 'clients'
  
  const isMobile = useIsMobile();
  const ITEMS_PER_PAGE = isMobile ? 3 : 10; // Menos itens por página no mobile

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // Adicionar estado para status das instâncias dos clientes
  const [clientInstanceStatus, setClientInstanceStatus] = useState({}); // { [instanceId]: status }

  /**
   * Busca a lista de usuários da API.
   */
  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE_URL}/api/usuarios/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Lidar com resposta paginada
      const data = response.data.results || response.data;
      setUsers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Erro ao buscar usuários:', error);
      setUsers([]);
      toast({
        title: "Erro",
        description: "Falha ao carregar usuários.",
        variant: "destructive",
      });
    }
  };

  /**
   * Busca a lista de clientes da API.
   */
  const fetchClients = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE_URL}/api/clientes/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Lidar com resposta paginada
      const data = response.data.results || response.data;
      setClients(Array.isArray(data) ? data : []);
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

  // Buscar status das instâncias dos clientes ao carregar clientes
  useEffect(() => {
    async function fetchStatuses() {
      const statusMap = {};
      for (const client of clients) {
        if (client.wapi_instance_id) {
          try {
            const token = getTokenForInstance(client.wapi_instance_id);
            const statusData = await getInstanceStatus(token, client.wapi_instance_id);
            statusMap[client.id] = statusData.status || statusData.connectionStatus || 'desconhecido';
          } catch (e) {
            statusMap[client.id] = 'desconectado';
          }
        } else {
          statusMap[client.id] = 'nao_conectado';
        }
      }
      setClientInstanceStatus(statusMap);
    }
    if (clients.length > 0) fetchStatuses();
  }, [clients]);

  // Polling automático para atualizar status das instâncias dos clientes a cada 10 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      async function fetchStatusesAndClients() {
        await fetchClients(); // Atualiza a lista de clientes do backend
        const updatedClients = Array.isArray(clients) ? clients : [];
        const statusMap = {};
        for (const client of updatedClients) {
          if (client.wapi_instance_id) {
            try {
              const token = getTokenForInstance(client.wapi_instance_id);
              const statusData = await getInstanceStatus(token, client.wapi_instance_id);
              statusMap[client.id] = statusData.status || statusData.connectionStatus || 'desconhecido';
            } catch (e) {
              statusMap[client.id] = 'desconectado';
            }
          } else {
            statusMap[client.id] = 'nao_conectado';
          }
        }
        setClientInstanceStatus(statusMap);
      }
      if (clients.length > 0) fetchStatusesAndClients();
    }, 10000); // 10 segundos
    return () => clearInterval(interval);
  }, [clients]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      
      // Carregar dados baseado no tipo de usuário
      if (canCreateClients()) {
        // Admin vê tudo
        await Promise.all([fetchUsers(), fetchClients()]);
      } else if (isCliente()) {
        // Cliente vê apenas usuários (colaboradores) e não clientes
        await fetchUsers();
        setClients([]); // Cliente não vê outros clientes
      } else if (isColaborador()) {
        // Colaborador não deveria estar aqui, mas por segurança
        setUsers([]);
        setClients([]);
      }
      
      setLoading(false);
    };
    loadData();
  }, [isAdmin, isCliente, isColaborador]);

  // Resetar páginas quando os dados mudarem
  useEffect(() => {
    setCurrentUserPage(0);
  }, [users.length]);

  useEffect(() => {
    setCurrentClientPage(0);
  }, [clients.length]);

  /**
   * Abre o modal de usuário para adição ou edição.
   * @param {object} user - Objeto de usuário para edição (opcional).
   */
  const openUserModal = (user = null) => {
    setEditingUser(user);
    setIsUserModalOpen(true);
  };

  /**
   * Abre o modal de cliente para adição ou edição.
   * @param {object} client - Objeto de cliente para edição (opcional).
   */
  const openClientModal = (client = null) => {
    setEditingClient(client);
    setIsClientModalOpen(true);
  };

  /**
   * Abre o modal de conexão W-APi para um cliente específico.
   * @param {object} client - Objeto do cliente a ser conectado.
   */
  const openConnectWapiModal = (client) => {
    setSelectedClientForWapi(client);
    setWapiInstanceId(client.wapi_instance_id || '');
    setWapiToken(client.wapi_token || '');
    setIsConnectWapiModalOpen(true);
  };

  /**
   * Lida com o envio do formulário de usuário.
   * @param {Event} e - Evento de formulário.
   */
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const userData = Object.fromEntries(formData.entries());

    try {
      const token = localStorage.getItem('access_token');
      if (editingUser) {
        await axios.put(`${API_BASE_URL}/api/usuarios/${editingUser.id}/`, userData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        toast({
          title: "Sucesso",
          description: "Usuário atualizado com sucesso.",
        });
      } else {
        await axios.post(`${API_BASE_URL}/api/usuarios/`, userData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        toast({
          title: "Sucesso",
          description: "Usuário adicionado com sucesso.",
        });
      }
      fetchUsers();
      setIsUserModalOpen(false);
    } catch (error) {
      console.error('Erro ao salvar usuário:', error);
      toast({
        title: "Erro",
        description: `Falha ao salvar usuário: ${error.response?.data?.detail || error.message}`,
        variant: "destructive",
      });
    }
  };

  /**
   * Lida com o envio do formulário de cliente.
   * @param {Event} e - Evento de formulário.
   */
  const handleClientSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const clientData = Object.fromEntries(formData.entries());

    // Validação básica no frontend
    if (!clientData.nome || !clientData.email) {
      toast({
        title: "Erro",
        description: "Nome e email são obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    // Verificar se o email já existe (apenas para criação)
    if (!editingClient) {
      const existingClient = clients.find(client => client.email === clientData.email);
      if (existingClient) {
        toast({
          title: "Erro",
          description: "Já existe um cliente cadastrado com este email.",
          variant: "destructive",
        });
        return;
      }
    }

    try {
      const token = localStorage.getItem('access_token');
      if (editingClient) {
        await axios.put(`${API_BASE_URL}/api/clientes/${editingClient.id}/`, clientData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        toast({
          title: "Sucesso",
          description: "Cliente atualizado com sucesso.",
        });
      } else {
        await axios.post(`${API_BASE_URL}/api/clientes/`, clientData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        toast({
          title: "Sucesso",
          description: "Cliente adicionado com sucesso.",
        });
      }
      fetchClients();
      setIsClientModalOpen(false);
    } catch (error) {
      console.error('Erro ao salvar cliente:', error);
      
      // Melhorar tratamento de erros
      let errorMessage = "Falha ao salvar cliente.";
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          // Se for um objeto com erros de validação
          const errors = Object.values(error.response.data).flat();
          errorMessage = errors.join(', ');
        } else {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  /**
   * Lida com a conexão W-APi para o cliente selecionado.
   */
  const handleConnectWapi = async () => {
    if (!selectedClientForWapi) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API_BASE_URL}/api/clientes/${selectedClientForWapi.id}/conectar_wapi/`, {
        instance_id: wapiInstanceId,
        token: wapiToken,
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      toast({
        title: "Sucesso",
        description: "Cliente conectado ao W-APi com sucesso!",
      });
      fetchClients(); // Atualiza a lista de clientes para refletir a conexão
      setIsConnectWapiModalOpen(false);
    } catch (error) {
      console.error('Erro ao conectar W-APi:', error);
      toast({
        title: "Erro",
        description: `Falha ao conectar W-APi: ${error.response?.data?.detail || error.message}`,
        variant: "destructive",
      });
    }
  };

  /**
   * Exclui um usuário.
   * @param {number} userId - ID do usuário a ser excluído.
   */
  const deleteUser = async (userId) => {
    if (!window.confirm('Tem certeza que deseja excluir este usuário?')) return;
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`${API_BASE_URL}/api/usuarios/${userId}/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      toast({
        title: "Sucesso",
        description: "Usuário excluído com sucesso.",
      });
      fetchUsers();
    } catch (error) {
      console.error('Erro ao excluir usuário:', error);
      toast({
        title: "Erro",
        description: `Falha ao excluir usuário: ${error.response?.data?.detail || error.message}`,
        variant: "destructive",
      });
    }
  };

  /**
   * Exclui um cliente.
   * @param {number} clientId - ID do cliente a ser excluído.
   */
  const deleteClient = async (clientId) => {
    if (!window.confirm('Tem certeza que deseja excluir este cliente?')) return;
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`${API_BASE_URL}/api/clientes/${clientId}/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      toast({
        title: "Sucesso",
        description: "Cliente excluído com sucesso.",
      });
      fetchClients();
    } catch (error) {
      console.error('Erro ao excluir cliente:', error);
      toast({
        title: "Erro",
        description: `Falha ao excluir cliente: ${error.response?.data?.detail || error.message}`,
        variant: "destructive",
      });
    }
  };

  /**
   * Calcula os dados paginados para usuários
   */
  const getPaginatedUsers = () => {
    const startIndex = currentUserPage * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    return users.slice(startIndex, endIndex);
  };

  /**
   * Calcula os dados paginados para clientes
   */
  const getPaginatedClients = () => {
    const startIndex = currentClientPage * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    return clients.slice(startIndex, endIndex);
  };

  /**
   * Calcula o número total de páginas para usuários
   */
  const getTotalUserPages = () => Math.ceil(users.length / ITEMS_PER_PAGE);

  /**
   * Calcula o número total de páginas para clientes
   */
  const getTotalClientPages = () => Math.ceil(clients.length / ITEMS_PER_PAGE);

  /**
   * Componente de navegação móvel
   */
  const MobileNavigation = () => {
    if (!isMobile) return null;

    return (
      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50">
        <div className="bg-background border rounded-lg shadow-lg p-2 flex gap-2">
          <Button
            variant={activeTab === 'users' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('users')}
            className="text-xs"
          >
            Usuários ({users.length})
          </Button>
          <Button
            variant={activeTab === 'clients' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('clients')}
            className="text-xs"
          >
            Clientes ({clients.length})
          </Button>
        </div>
      </div>
    );
  };

  /**
   * Componente de paginação
   */
  const Pagination = ({ currentPage, totalPages, onPageChange, type, totalItems, currentItems }) => {
    if (totalPages <= 1) return null;

    return (
      <div className="flex flex-col items-center gap-2 mt-4">
        <div className="text-sm text-muted-foreground text-center">
          Mostrando {currentItems} de {totalItems} {type === 'users' ? 'usuários' : 'clientes'}
        </div>
        <div className="flex justify-center items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 0}
          >
            Anterior
          </Button>
          <span className="text-sm text-muted-foreground">
            Página {currentPage + 1} de {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages - 1}
          >
            Próxima
          </Button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className={`${isMobile ? 'pb-20' : ''} p-6 flex justify-center items-center h-64`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando dados...</p>
          {isMobile && (
            <p className="mt-2 text-sm text-gray-500">Preparando interface móvel...</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border p-6">
        <h1 className="text-3xl font-bold">Gerenciamento de Usuários e Clientes</h1>
      </div>

      {/* Conteúdo com scroll */}
      <div className="p-6 space-y-6 overflow-y-auto">
        {/* Estatísticas rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-blue-50 dark:bg-blue-950/20">
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">{users.length}</div>
              <div className="text-sm text-muted-foreground">
                {isAdmin() ? 'Total de Usuários' : 'Total de Colaboradores'}
              </div>
            </CardContent>
          </Card>
          {canCreateClients() && (
            <>
              <Card className="bg-green-50 dark:bg-green-950/20">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-green-600">{clients.length}</div>
                  <div className="text-sm text-muted-foreground">Total de Clientes</div>
                </CardContent>
              </Card>
              <Card className="bg-purple-50 dark:bg-purple-950/20">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-purple-600">
                    {clients.filter(client => client.wapi_instance_id).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Clientes Conectados</div>
                </CardContent>
              </Card>
            </>
          )}
          {isCliente() && (
            <>
              <Card className="bg-green-50 dark:bg-green-950/20">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-green-600">
                    {users.filter(user => user.tipo_usuario === 'colaborador').length}
                  </div>
                  <div className="text-sm text-muted-foreground">Colaboradores Ativos</div>
                </CardContent>
              </Card>
              <Card className="bg-purple-50 dark:bg-purple-950/20">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-purple-600">
                    {users.filter(user => user.tipo_usuario === 'admin').length}
                  </div>
                  <div className="text-sm text-muted-foreground">Administradores</div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Abas baseadas no tipo de usuário */}
        {canCreateClients() && (
          <div className="flex gap-2 mb-4 mt-4">
            <Button
              variant={activeTab === 'users' ? 'default' : 'outline'}
              onClick={() => setActiveTab('users')}
              className="flex-1"
            >
              Usuários ({users.length})
            </Button>
            <Button
              variant={activeTab === 'clients' ? 'default' : 'outline'}
              onClick={() => setActiveTab('clients')}
              className="flex-1"
            >
              Clientes ({clients.length})
            </Button>
          </div>
        )}
        
        {/* Para clientes, mostrar apenas usuários */}
        {isCliente() && (
          <div className="mb-4 mt-4">
            <h2 className="text-xl font-semibold">Gerenciar Colaboradores</h2>
            <p className="text-muted-foreground">Gerencie os colaboradores da sua empresa.</p>
          </div>
        )}

        {/* Seção de Gerenciamento de Usuários */}
        {(activeTab === 'users' || isCliente()) && (
          <Card>
            <CardHeader>
              <CardTitle>{isAdmin() ? 'Usuários' : 'Colaboradores'}</CardTitle>
              <CardDescription>
                {isAdmin() 
                  ? 'Gerencie os usuários que acessam o sistema.' 
                  : 'Gerencie os colaboradores da sua empresa.'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => openUserModal()}>
                {isAdmin() ? 'Adicionar Usuário' : 'Adicionar Colaborador'}
              </Button>
              {/* Tabela responsiva */}
              <div className="mt-4 overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Cliente</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {getPaginatedUsers().length > 0 ? (
                      getPaginatedUsers().map((user) => (
                        <TableRow key={user.id}>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{user.nome}</TableCell>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{user.email}</TableCell>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{user.tipo_usuario}</TableCell>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{user.cliente_nome}</TableCell>
                          <TableCell>
                            <div className={isMobile ? 'flex flex-col gap-1' : 'flex gap-2'}>
                              <Button variant="outline" size="sm" onClick={() => openUserModal(user)} className={isMobile ? 'text-xs' : ''} title="Editar">
                                <Pencil className="w-4 h-4" />
                              </Button>
                              <Button variant="destructive" size="sm" onClick={() => deleteUser(user.id)} className={isMobile ? 'text-xs' : ''} title="Excluir">
                                <Trash className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center text-gray-500">
                          Nenhum usuário encontrado
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
              {/* Paginação para usuários */}
              <Pagination
                currentPage={currentUserPage}
                totalPages={getTotalUserPages()}
                onPageChange={setCurrentUserPage}
                type="users"
                totalItems={users.length}
                currentItems={getPaginatedUsers().length}
              />
            </CardContent>
          </Card>
        )}

        {/* Seção de Gerenciamento de Clientes - Apenas para Administradores */}
        {activeTab === 'clients' && canCreateClients() && (
          <Card>
            <CardHeader>
              <CardTitle>Clientes</CardTitle>
              <CardDescription>Gerencie os clientes e suas configurações de W-APi.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => openClientModal()}>Adicionar Cliente</Button>
              {/* Tabela responsiva */}
              <div className="mt-4 overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Empresa</TableHead>
                      <TableHead>Instância W-APi</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {getPaginatedClients().length > 0 ? (
                      getPaginatedClients().map((client) => (
                        <TableRow key={client.id}>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{client.nome}</TableCell>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{client.email}</TableCell>
                          <TableCell className={isMobile ? 'text-sm' : ''}>{client.empresa}</TableCell>
                          <TableCell className={isMobile ? 'text-sm' : ''}>
                            {client.whatsapp_status === 'conectado' ? (
                              <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200"><Wifi className="w-3 h-3 mr-1" />Conectado</Badge>
                            ) : client.whatsapp_status === 'desconectado' ? (
                              <Badge variant="outline" className="bg-red-100 text-red-800 border-red-200"><WifiOff className="w-3 h-3 mr-1" />Desconectado</Badge>
                            ) : (
                              <Badge variant="outline" className="bg-gray-100 text-gray-800 border-gray-200">{client.whatsapp_status || 'Verificando...'}</Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className={isMobile ? 'flex flex-col gap-1' : 'flex gap-2'}>
                              <Button variant="outline" size="sm" onClick={() => openClientModal(client)} className={isMobile ? 'text-xs' : ''} title="Editar">
                                <Pencil className="w-4 h-4" />
                              </Button>
                              <Button variant="outline" size="sm" onClick={() => openConnectWapiModal(client)} className={isMobile ? 'text-xs' : ''}>
                                Conectar Instância WhatsApp
                              </Button>
                              <Button variant="destructive" size="sm" onClick={() => deleteClient(client.id)} className={isMobile ? 'text-xs' : ''} title="Excluir">
                                <Trash className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center text-gray-500">
                          Nenhum cliente encontrado
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
              {/* Paginação para clientes */}
              <Pagination
                currentPage={currentClientPage}
                totalPages={getTotalClientPages()}
                onPageChange={setCurrentClientPage}
                type="clients"
                totalItems={clients.length}
                currentItems={getPaginatedClients().length}
              />
            </CardContent>
          </Card>
        )}

        {/* Navegação móvel flutuante */}
        <MobileNavigation />

        {/* Modal de Usuário */}
        <Dialog open={isUserModalOpen} onOpenChange={setIsUserModalOpen}>
          <DialogContent className={isMobile ? 'w-[95vw] max-w-none' : ''}>
            <DialogHeader>
              <DialogTitle>{editingUser ? 'Editar Usuário' : 'Adicionar Usuário'}</DialogTitle>
              <DialogDescription>Preencha os detalhes do usuário.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleUserSubmit} className="space-y-4">
              <div>
                <Label htmlFor="nome">Nome</Label>
                <Input id="nome" name="nome" defaultValue={editingUser?.nome || ''} required />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" name="email" type="email" defaultValue={editingUser?.email || ''} required />
              </div>
              <div>
                <Label htmlFor="telefone">Telefone</Label>
                <Input id="telefone" name="telefone" defaultValue={editingUser?.telefone || ''} />
              </div>
              {isAdmin() ? (
                <div>
                  <Label htmlFor="tipo_usuario">Tipo de Usuário</Label>
                  <Select name="tipo_usuario" defaultValue={editingUser?.tipo_usuario || 'colaborador'}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Administrador</SelectItem>
                      <SelectItem value="cliente">Cliente</SelectItem>
                      <SelectItem value="colaborador">Colaborador</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              ) : (
                // Para clientes, o tipo é sempre colaborador
                <input type="hidden" name="tipo_usuario" value="colaborador" />
              )}
              {isAdmin() ? (
                <div>
                  <Label htmlFor="cliente">Cliente</Label>
                  <Select name="cliente" defaultValue={editingUser?.cliente || ''} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um cliente" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients && clients.length > 0 ? (
                        clients.map(client => (
                          client.id ? (
                            <SelectItem key={client.id} value={client.id.toString()}>{client.nome}</SelectItem>
                          ) : null
                        ))
                      ) : (
                        <SelectItem value="no-clients" disabled>Nenhum cliente disponível</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>
              ) : (
                // Para clientes, o campo cliente é preenchido automaticamente
                <input type="hidden" name="cliente" value={JSON.parse(localStorage.getItem('user'))?.cliente || ''} />
              )}
              {!editingUser && (
                <>
                  <div>
                    <Label htmlFor="password">Senha</Label>
                    <Input id="password" name="password" type="password" required />
                  </div>
                  <div>
                    <Label htmlFor="confirmar_password">Confirmar Senha</Label>
                    <Input id="confirmar_password" name="confirmar_password" type="password" required />
                  </div>
                </>
              )}
              <DialogFooter className={isMobile ? 'flex-col gap-2' : ''}>
                <Button type="button" variant="outline" onClick={() => setIsUserModalOpen(false)} className={isMobile ? 'w-full' : ''}>
                  Cancelar
                </Button>
                <Button type="submit" className={isMobile ? 'w-full' : ''}>Salvar</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Modal de Cliente */}
        <Dialog open={isClientModalOpen} onOpenChange={setIsClientModalOpen}>
          <DialogContent className={isMobile ? 'w-[95vw] max-w-none' : ''}>
            <DialogHeader>
              <DialogTitle>{editingClient ? 'Editar Cliente' : 'Adicionar Cliente'}</DialogTitle>
              <DialogDescription>Preencha os detalhes do cliente.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleClientSubmit} className="space-y-4">
              <div>
                <Label htmlFor="nome">Nome</Label>
                <Input id="nome" name="nome" defaultValue={editingClient?.nome || ''} required />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" name="email" type="email" defaultValue={editingClient?.email || ''} required />
              </div>
              <div>
                <Label htmlFor="telefone">Telefone</Label>
                <Input id="telefone" name="telefone" defaultValue={editingClient?.telefone || ''} />
              </div>
              <div>
                <Label htmlFor="empresa">Empresa</Label>
                <Input id="empresa" name="empresa" defaultValue={editingClient?.empresa || ''} />
              </div>
              <DialogFooter className={isMobile ? 'flex-col gap-2' : ''}>
                <Button type="button" variant="outline" onClick={() => setIsClientModalOpen(false)} className={isMobile ? 'w-full' : ''}>
                  Cancelar
                </Button>
                <Button type="submit" className={isMobile ? 'w-full' : ''}>Salvar</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Modal de Conexão W-APi */}
        <Dialog open={isConnectWapiModalOpen} onOpenChange={setIsConnectWapiModalOpen}>
          <DialogContent className={isMobile ? 'w-[95vw] max-w-none' : ''}>
            <DialogHeader>
              <DialogTitle>Conectar Instância WhatsApp para {selectedClientForWapi?.nome}</DialogTitle>
              <DialogDescription>Insira os detalhes da instância W-APi.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="wapi_instance_id">ID da Instância WhatsApp</Label>
                <Input
                  id="wapi_instance_id"
                  value={wapiInstanceId}
                  onChange={(e) => setWapiInstanceId(e.target.value)}
                  placeholder="Ex: 3B6XIW-ZTS923-GEAY6V"
                />
              </div>
              <div>
                <Label htmlFor="wapi_token">Token WhatsApp</Label>
                <Input
                  id="wapi_token"
                  value={wapiToken}
                  onChange={(e) => setWapiToken(e.target.value)}
                  placeholder="Ex: Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
                />
              </div>
              <DialogFooter className={isMobile ? 'flex-col gap-2' : ''}>
                <Button type="button" variant="outline" onClick={() => setIsConnectWapiModalOpen(false)} className={isMobile ? 'w-full' : ''}>
                  Cancelar
                </Button>
                <Button onClick={handleConnectWapi} className={isMobile ? 'w-full' : ''}>Conectar</Button>
              </DialogFooter>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

export default UserManagement;



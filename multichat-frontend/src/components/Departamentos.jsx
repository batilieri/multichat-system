import React, { useState, useEffect } fromreact';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card;
import { Button } from './ui/button';
import [object Object]Input } from './ui/input';
import [object Object]Label } from './ui/label;
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog;
import [object Object] Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import [object Object]Badge } from './ui/badge';
import [object Object]toast } from ./ui/use-toast';
import { Plus, Pencil, Trash, Building } from 'lucide-react';
import { useAuth } from../contexts/AuthContext;const API_BASE_URL = http://localhost:8000';

function Departamentos() {
  const { isAdmin, isCliente } = useAuth();
  const [departamentos, setDepartamentos] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDepartamento, setEditingDepartamento] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() =>[object Object]fetchDepartamentos();
  }, []);

  const fetchDepartamentos = async () =>[object Object] try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/departamentos/`, [object Object]       headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDepartamentos(data);
      } else {
        throw new Error('Erro ao carregar departamentos');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast([object Object]        title: "Erro",
        description: Falhaao carregar departamentos,
        variant: "destructive, });
    } finally [object Object]  setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const departamentoData = Object.fromEntries(formData.entries());

    try {
      const token = localStorage.getItem('access_token');
      const url = editingDepartamento 
        ? `${API_BASE_URL}/api/departamentos/${editingDepartamento.id}/`
        : `${API_BASE_URL}/api/departamentos/`;
      
      const method = editingDepartamento ? 'PUT' : 'POST';
      
      const response = await fetch(url, [object Object]   method,
        headers: {
          Authorization: `Bearer ${token}`,
         Content-Type':application/json',
        },
        body: JSON.stringify(departamentoData),
      });

      if (response.ok) [object Object] toast([object Object]          title: "Sucesso",
          description: editingDepartamento 
            ? "Departamento atualizado com sucesso"
            :Departamento criado com sucesso",
        });
        fetchDepartamentos();
        setIsModalOpen(false);
        setEditingDepartamento(null);
      } else {
        throw new Error('Erro ao salvar departamento');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast([object Object]        title: "Erro",
        description: "Falha ao salvar departamento,
        variant: "destructive",
      });
    }
  };

  const deleteDepartamento = async (id) =>[object Object]  if (!window.confirm('Tem certeza que deseja excluir este departamento?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/departamentos/${id}/`,[object Object]
        method:DELETE,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) [object Object] toast([object Object]          title: "Sucesso",
          description: Departamento excluído com sucesso",
        });
        fetchDepartamentos();
      } else {
        throw new Error('Erro ao excluir departamento');
      }
    } catch (error) {
      console.error('Erro:', error);
      toast([object Object]        title: "Erro",
        description:Falha ao excluir departamento,
        variant: "destructive",
      });
    }
  };

  const openModal = (departamento = null) => {
    setEditingDepartamento(departamento);
    setIsModalOpen(true);
  };

  if (loading) {
    return (
      <div className=flex items-center justify-center h-64    <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto></div>
          <p className="mt-2t-muted-foreground">Carregando departamentos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className=space-y-6">
      <div className=flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground>Departamentos</h1>
          <p className="text-muted-foreground>            Gerencie os departamentos da sua empresa
          </p>
        </div>
       [object Object](isAdmin() || isCliente()) && (
          <Button onClick={() => openModal()} className=flexitems-center space-x-2
            <Plus className="h-4 w-4 />
            <span>Novo Departamento</span>
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className=flexitems-center space-x-2         <Building className="h-5 w-5 />
            <span>Lista de Departamentos</span>
          </CardTitle>
          <CardDescription>
            {departamentos.length} departamento(s) encontrado(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {departamentos.length >0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className=text-right>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {departamentos.map((departamento) => (
                  <TableRow key={departamento.id}>
                    <TableCell className="font-medium">
                      {departamento.nome}
                    </TableCell>
                    <TableCell>{departamento.cliente}</TableCell>
                    <TableCell>
                      <Badge variant={departamento.ativo ? "default :                [object Object]departamento.ativo ? Ativo" : "Inativo"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openModal(departamento)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => deleteDepartamento(departamento.id)}
                        >
                          <Trash className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8>         <Building className="h-1212t-muted-foreground mx-auto mb-4/>
              <h3 className="text-lg font-medium text-muted-foreground mb-2>
                Nenhum departamento encontrado
              </h3>
              <p className="text-muted-foreground mb-4>
                Crie seu primeiro departamento para organizar sua equipe
              </p>
             [object Object](isAdmin() || isCliente()) && (
                <Button onClick={() => openModal()}>
                  <Plus className=h-4 w-4 mr-2
                  Criar Departamento
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de Departamento */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingDepartamento ? 'Editar Departamento' : Novo Departamento'}
            </DialogTitle>
            <DialogDescription>
              {editingDepartamento 
                ? 'Edite as informações do departamento'
                : 'Crie um novo departamento para organizar sua equipe     }
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4>
            <div>
              <Label htmlFor="nome">Nome do Departamento</Label>
              <Input
                id="nome"
                name="nome"
                defaultValue={editingDepartamento?.nome || '}       placeholder="Ex: Suporte, Vendas, Marketing"
                required
              />
            </div>
            <DialogFooter>
              <Button type=button variant="outline" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit>
                {editingDepartamento ? Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default Departamentos; 
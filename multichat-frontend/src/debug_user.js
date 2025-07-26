// Script de debug para verificar dados do usuário
// Execute no console do navegador

console.log('=== DEBUG USUÁRIO ===');

// Verificar dados no localStorage
const userData = localStorage.getItem('user');
console.log('Dados do usuário no localStorage:', userData);

if (userData) {
  const user = JSON.parse(userData);
  console.log('Usuário parseado:', user);
  console.log('Tipo de usuário:', user.tipo_usuario);
  console.log('É superuser:', user.is_superuser);
  
  // Verificar funções de permissão
  const isAdmin = () => {
    return user && (user.is_superuser || user.tipo_usuario === 'admin')
  }
  
  const isCliente = () => {
    return user && user.tipo_usuario === 'cliente'
  }
  
  const isColaborador = () => {
    return user && user.tipo_usuario === 'colaborador'
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
  
  console.log('=== RESULTADOS DAS PERMISSÕES ===');
  console.log('isAdmin():', isAdmin());
  console.log('isCliente():', isCliente());
  console.log('isColaborador():', isColaborador());
  console.log('canAccessReports():', canAccessReports());
  console.log('canAccessSettings():', canAccessSettings());
  console.log('canAccessWhatsApp():', canAccessWhatsApp());
  console.log('canAccessUsers():', canAccessUsers());
} else {
  console.log('❌ Nenhum usuário encontrado no localStorage');
}

console.log('=== FIM DEBUG ==='); 
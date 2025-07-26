/**
 * Hook para sistema de toast/notificações moderno.
 * 
 * Fornece uma função toast para exibir notificações temporárias
 * na interface do usuário sem necessidade de interação.
 */

// Sistema de toast moderno com notificações temporárias
export const toast = ({ title, description, variant = "default" }) => {
  const message = `${title}: ${description}`;
  
  // Criar elemento de toast
  const toastElement = document.createElement('div');
  toastElement.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;
  
  // Estilos baseados na variante
  if (variant === "destructive") {
    toastElement.className += ' bg-red-500 text-white';
    toastElement.innerHTML = `
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
        </svg>
        <div>
          <div class="font-medium">${title}</div>
          <div class="text-sm opacity-90">${description}</div>
        </div>
      </div>
    `;
  } else {
    toastElement.className += ' bg-green-500 text-white';
    toastElement.innerHTML = `
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
        </svg>
        <div>
          <div class="font-medium">${title}</div>
          <div class="text-sm opacity-90">${description}</div>
        </div>
      </div>
    `;
  }
  
  // Adicionar ao DOM
  document.body.appendChild(toastElement);
  
  // Animar entrada
  setTimeout(() => {
    toastElement.classList.remove('translate-x-full');
  }, 100);
  
  // Auto-remover após 3 segundos
  setTimeout(() => {
    toastElement.classList.add('translate-x-full');
    setTimeout(() => {
      if (toastElement.parentNode) {
        toastElement.parentNode.removeChild(toastElement);
      }
    }, 300);
  }, 3000);
  
  // Log para desenvolvimento
  if (variant === "destructive") {
    console.error(`❌ ${message}`);
  } else {
    console.log(`✅ ${message}`);
  }
};

// Hook que retorna a função toast
export const useToast = () => {
  return { toast };
};

export default useToast;


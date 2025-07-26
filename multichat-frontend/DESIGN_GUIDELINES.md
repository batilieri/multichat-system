# 🎨 Design Guidelines - MultiChat System

## 📋 Visão Geral

Este documento define os padrões de design utilizados no MultiChat System, garantindo consistência visual e experiência do usuário em toda a aplicação.

## 🎯 Princípios de Design

### **1. Simplicidade e Clareza**
- Interface limpa e minimalista
- Hierarquia visual clara
- Foco na usabilidade

### **2. Responsividade**
- Design mobile-first
- Adaptação para diferentes tamanhos de tela
- Componentes flexíveis

### **3. Acessibilidade**
- Contraste adequado
- Navegação por teclado
- Textos legíveis

## 🎨 Sistema de Cores

### **Paleta Principal (OKLCH)**
```css
/* Cores de Fundo */
--background: oklch(1 0 0) (light) / oklch(0.145 0 0) (dark)
--card: oklch(1 0 0) (light) / oklch(0.205 0 0) (dark)
--popover: oklch(1 0 0) (light) / oklch(0.205 0 0) (dark)

/* Cores de Texto */
--foreground: oklch(0.145 0 0) (light) / oklch(0.985 0 0) (dark)
--muted-foreground: oklch(0.556 0 0) (light) / oklch(0.708 0 0) (dark)

/* Cores Primárias */
--primary: oklch(0.205 0 0) (light) / oklch(0.922 0 0) (dark)
--primary-foreground: oklch(0.985 0 0) (light) / oklch(0.205 0 0) (dark)

/* Cores de Estado */
--destructive: oklch(0.577 0.245 27.325) (light) / oklch(0.704 0.191 22.216) (dark)
--destructive-foreground: #ffffff

/* Cores de Interface */
--border: oklch(0.922 0 0) (light) / oklch(1 0 0 / 10%) (dark)
--input: oklch(0.922 0 0) (light) / oklch(1 0 0 / 15%) (dark)
--ring: oklch(0.708 0 0) (light) / oklch(0.556 0 0) (dark)
--accent: oklch(0.97 0 0) (light) / oklch(0.269 0 0) (dark)
--accent-foreground: oklch(0.205 0 0) (light) / oklch(0.985 0 0) (dark)
```

### **Cores da Sidebar**
```css
--sidebar: oklch(0.985 0 0) (light) / oklch(0.205 0 0) (dark)
--sidebar-border: oklch(0.922 0 0) (light) / oklch(1 0 0 / 10%) (dark)
--sidebar-foreground: oklch(0.145 0 0) (light) / oklch(0.985 0 0) (dark)
--sidebar-primary: oklch(0.205 0 0) (light) / oklch(0.488 0.243 264.376) (dark)
--sidebar-primary-foreground: oklch(0.985 0 0) (light) / oklch(0.985 0 0) (dark)
--sidebar-accent: oklch(0.97 0 0) (light) / oklch(0.269 0 0) (dark)
--sidebar-accent-foreground: oklch(0.205 0 0) (light) / oklch(0.985 0 0) (dark)
```

### **Cores de Gráficos**
```css
--chart-1: oklch(0.646 0.222 41.116) (light) / oklch(0.488 0.243 264.376) (dark)
--chart-2: oklch(0.6 0.118 184.704) (light) / oklch(0.696 0.17 162.48) (dark)
--chart-3: oklch(0.398 0.07 227.392) (light) / oklch(0.769 0.188 70.08) (dark)
--chart-4: oklch(0.828 0.189 84.429) (light) / oklch(0.627 0.265 303.9) (dark)
--chart-5: oklch(0.769 0.188 70.08) (light) / oklch(0.645 0.246 16.439) (dark)
```

## 📐 Tipografia

### **Hierarquia de Texto**
```css
/* Títulos */
h1: text-3xl font-bold text-foreground
h2: text-2xl font-bold text-foreground
h3: text-xl font-semibold text-foreground

/* Texto do Corpo */
p: text-sm text-foreground
p.muted: text-sm text-muted-foreground

/* Texto Pequeno */
.text-xs: text-xs text-muted-foreground
```

### **Fontes**
- **Família**: Inter, system-ui, sans-serif
- **Pesos**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## 🧩 Componentes Base

### **1. Botões (shadcn/ui)**

#### **Botão Padrão**
```jsx
import { Button } from './ui/button'

<Button variant="default" size="default">
  Texto do Botão
</Button>
```

#### **Variantes de Botão**
```jsx
// Primário (padrão)
<Button variant="default">Primário</Button>

// Secundário
<Button variant="secondary">Secundário</Button>

// Outline
<Button variant="outline">Outline</Button>

// Destrutivo
<Button variant="destructive">Excluir</Button>

// Ghost
<Button variant="ghost">Ghost</Button>

// Link
<Button variant="link">Link</Button>
```

#### **Tamanhos de Botão**
```jsx
<Button size="sm">Pequeno</Button>
<Button size="default">Padrão</Button>
<Button size="lg">Grande</Button>
<Button size="icon">Ícone</Button>
```

#### **Botão com Animações (Framer Motion)**
```jsx
import { motion } from 'framer-motion'

<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring transition-all duration-200"
>
  Texto do Botão
</motion.button>
```

### **2. Inputs**

#### **Input Padrão (shadcn/ui)**
```jsx
import { Input } from './ui/input'

<Input
  type="text"
  placeholder="Digite aqui..."
  className="w-full"
/>
```

#### **Input Customizado**
```jsx
<input
  className="w-full px-3 py-3 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
  placeholder="Digite aqui..."
/>
```

#### **Input com Ícone**
```jsx
<div className="relative">
  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
  <input
    className="w-full pl-10 pr-4 py-2 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
    placeholder="Buscar..."
  />
</div>
```

### **3. Cards (shadcn/ui)**

#### **Card Padrão**
```jsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './ui/card'

<Card className="bg-card border border-border rounded-xl shadow-sm">
  <CardHeader>
    <CardTitle>Título do Card</CardTitle>
    <CardDescription>Descrição do card</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Conteúdo do Card */}
  </CardContent>
  <CardFooter>
    {/* Footer do Card */}
  </CardFooter>
</Card>
```

#### **Card com Animações**
```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  whileHover={{ scale: 1.02 }}
  className="bg-card border border-border rounded-lg p-6 shadow-sm"
>
  {/* Conteúdo do Card */}
</motion.div>
```

#### **Card de Estatística**
```jsx
<div className="bg-card border border-border rounded-lg p-6 shadow-sm">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-muted-foreground text-sm font-medium">{title}</p>
      <p className="text-2xl font-bold text-foreground mt-1">{value}</p>
    </div>
    <div className="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/20">
      <Icon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
    </div>
  </div>
</div>
```

### **4. Menus e Dropdowns**

#### **Menu de Notificações**
```jsx
<motion.div
  initial={{ opacity: 0, y: 10, scale: 0.95 }}
  animate={{ opacity: 1, y: 0, scale: 1 }}
  exit={{ opacity: 0, y: 10, scale: 0.95 }}
  className="absolute right-0 mt-2 w-80 bg-popover border border-border rounded-lg shadow-lg z-50"
>
  {/* Conteúdo do Menu */}
</motion.div>
```

#### **Dropdown Menu (shadcn/ui)**
```jsx
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu'

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Abrir Menu</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Opção 1</DropdownMenuItem>
    <DropdownMenuItem>Opção 2</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## 🎭 Animações

### **Framer Motion - Padrões**

#### **Entrada de Componentes**
```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  {/* Componente */}
</motion.div>
```

#### **Hover Effects**
```jsx
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  className="transition-all duration-200"
>
  {/* Botão */}
</motion.button>
```

#### **AnimatePresence para Menus**
```jsx
import { AnimatePresence } from 'framer-motion'

<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.95 }}
      transition={{ duration: 0.2 }}
    >
      {/* Menu */}
    </motion.div>
  )}
</AnimatePresence>
```

#### **Animações de Loading**
```jsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  className="flex items-center space-x-2"
>
  <Loader2 className="h-4 w-4 animate-spin" />
  <span>Carregando...</span>
</motion.div>
```

## 📱 Layout e Grid

### **Grid System**
```css
/* Grid Responsivo */
.grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6

/* Espaçamento Padrão */
space-y-6  /* Espaçamento vertical */
space-x-4  /* Espaçamento horizontal */
p-6        /* Padding */
px-6 py-4  /* Padding específico */
```

### **Container Padrão**
```jsx
<div className="p-6 space-y-6">
  {/* Conteúdo da Página */}
</div>
```

### **Layout de Página**
```jsx
<div className="min-h-screen flex">
  {/* Sidebar */}
  <Sidebar />
  
  {/* Conteúdo Principal */}
  <div className="flex-1 flex flex-col">
    <Header />
    <main className="flex-1 overflow-auto">
      {/* Conteúdo da página */}
    </main>
  </div>
</div>
```

## 🎨 Estados e Feedback

### **Estados de Loading**
```jsx
// Skeleton Loading
<div className="bg-card border border-border rounded-lg p-6 animate-pulse">
  <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
  <div className="h-8 bg-muted rounded w-3/4 mb-2"></div>
  <div className="h-4 bg-muted rounded w-1/3"></div>
</div>

// Loading com Spinner
<div className="flex items-center space-x-2">
  <Loader2 className="h-4 w-4 animate-spin" />
  <span>Carregando...</span>
</div>
```

### **Estados de Erro**
```jsx
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center space-x-2"
>
  <AlertCircle className="h-5 w-5 text-destructive" />
  <span className="text-sm text-destructive">{error}</span>
</motion.div>
```

### **Estados de Sucesso**
```jsx
<div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-2">
  <CheckCircle className="h-5 w-5 text-green-600" />
  <span className="text-sm text-green-800">Operação realizada com sucesso!</span>
</div>
```

## 🔧 Ícones

### **Biblioteca de Ícones**
- **Lucide React** - Ícones principais
- **Tamanhos Padrão**: h-4 w-4, h-5 w-5, h-6 w-6
- **Cores**: text-foreground, text-muted-foreground, text-primary

### **Uso Padrão**
```jsx
import { MessageCircle, Users, Settings } from 'lucide-react'

<MessageCircle className="h-5 w-5 text-foreground" />
```

## 🎨 Tema Escuro/Claro

### **Toggle de Tema**
```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  onClick={toggleTheme}
  className="p-2 rounded-lg hover:bg-accent transition-colors"
>
  {theme === 'light' ? (
    <Moon className="h-5 w-5 text-foreground" />
  ) : (
    <Sun className="h-5 w-5 text-foreground" />
  )}
</motion.button>
```

### **Variáveis CSS para Tema**
```css
/* Light Theme */
--background: oklch(1 0 0)
--foreground: oklch(0.145 0 0)
--card: oklch(1 0 0)
--border: oklch(0.922 0 0)

/* Dark Theme */
--background: oklch(0.145 0 0)
--foreground: oklch(0.985 0 0)
--card: oklch(0.205 0 0)
--border: oklch(1 0 0 / 10%)
```

## 📐 Espaçamentos e Tamanhos

### **Sistema de Espaçamento**
```css
/* Padding */
p-1: 0.25rem (4px)
p-2: 0.5rem (8px)
p-3: 0.75rem (12px)
p-4: 1rem (16px)
p-6: 1.5rem (24px)

/* Margin */
m-1: 0.25rem (4px)
m-2: 0.5rem (8px)
m-4: 1rem (16px)
m-6: 1.5rem (24px)

/* Gap */
gap-2: 0.5rem (8px)
gap-4: 1rem (16px)
gap-6: 1.5rem (24px)
```

### **Tamanhos de Componentes**
```css
/* Alturas Padrão */
h-8: 2rem (32px) - Botões pequenos
h-9: 2.25rem (36px) - Botões padrão
h-10: 2.5rem (40px) - Inputs
h-12: 3rem (48px) - Botões grandes

/* Larguras */
w-full: 100%
w-fit: fit-content
max-w-md: 28rem (448px)
max-w-lg: 32rem (512px)
```

## 🧩 Componentes Específicos

### **1. Mensagens de Chat**
```jsx
// Bolha de mensagem
const bubbleBase = `
  rounded-xl px-4 py-3 text-sm max-w-[75%] shadow-sm
  transition-all duration-200 relative
  ${isMe
    ? "bg-primary text-primary-foreground rounded-br-none hover:bg-primary/90"
    : "bg-card border border-border text-foreground rounded-bl-none hover:bg-accent"
  }
`

<motion.div 
  className={bubbleBase + ' w-fit'}
  whileHover={{ scale: 1.01 }}
  transition={{ duration: 0.2 }}
>
  {/* Conteúdo da mensagem */}
</motion.div>
```

### **2. Sidebar**
```jsx
<motion.div
  initial={false}
  animate={{
    width: collapsed ? 80 : 280
  }}
  transition={{ duration: 0.3, ease: "easeInOut" }}
  className="bg-sidebar border-r border-sidebar-border flex flex-col h-full relative"
>
  {/* Conteúdo da sidebar */}
</motion.div>
```

### **3. Header**
```jsx
<header className="bg-background border-b border-border px-6 py-4">
  <div className="flex items-center justify-between">
    {/* Busca */}
    <div className="relative max-w-md w-full">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <input
        className="w-full pl-10 pr-4 py-2 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
        placeholder="Buscar..."
      />
    </div>
    
    {/* Controles */}
    <div className="flex items-center space-x-4">
      {/* Toggle de tema, notificações, etc. */}
    </div>
  </div>
</header>
```

### **4. Dashboard Cards**
```jsx
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
```

## 🎯 Checklist de Implementação

### **Para Novos Componentes:**
- [ ] Usar os componentes shadcn/ui quando disponíveis
- [ ] Implementar animações com Framer Motion
- [ ] Adicionar estados de hover/focus
- [ ] Garantir responsividade
- [ ] Incluir loading states
- [ ] Adicionar feedback de erro/sucesso
- [ ] Testar em tema claro/escuro
- [ ] Verificar acessibilidade

### **Para Novas Páginas:**
- [ ] Usar o layout padrão (p-6 space-y-6)
- [ ] Implementar grid responsivo
- [ ] Adicionar header com título e descrição
- [ ] Incluir breadcrumbs se necessário
- [ ] Garantir consistência com outros componentes

## 📚 Recursos

### **Bibliotecas Utilizadas:**
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes base
- **Framer Motion** - Animações
- **Lucide React** - Ícones
- **React Router** - Navegação
- **Recharts** - Gráficos

### **Ferramentas de Desenvolvimento:**
- **Vite** - Build tool
- **ESLint** - Linting
- **Prettier** - Formatação

### **Estrutura de Arquivos:**
```
src/
├── components/
│   ├── ui/           # Componentes shadcn/ui
│   ├── Header.jsx    # Header da aplicação
│   ├── Sidebar.jsx   # Sidebar de navegação
│   ├── Dashboard.jsx # Dashboard principal
│   ├── Message.jsx   # Componente de mensagem
│   └── ...
├── contexts/
│   ├── AuthContext.jsx
│   └── ThemeContext.jsx
└── ...
```

---

**Última Atualização**: 2025-07-12  
**Versão**: 2.0.0  
**Mantido por**: Equipe de Design MultiChat 
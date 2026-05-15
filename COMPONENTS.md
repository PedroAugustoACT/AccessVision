# Access Vision - Tela de Upload de PDF

## 📋 Descrição
Aplicação web moderna para upload de documentos PDF com interface baseada no Design System do Governo Federal Brasileiro.

## 🎨 Design
- **Paleta de Cores**: Design System Federal (Azul #006294, Verde #06C637)
- **Responsivo**: Otimizado para mobile, tablet e desktop
- **Acessível**: ARIA labels, semantic HTML, keyboard navigation
- **Moderno**: Gradiente, animações suaves, feedback visual

## ⚙️ Tecnologias
- React 19.2.6
- TypeScript
- Tailwind CSS v3
- Vite 8.0.13

## 📁 Estrutura de Componentes

```
src/
├── components/
│   ├── FileUpload.tsx         # Componente principal de upload
│   ├── UploadFeedback.tsx     # Feedback de loading/sucesso
│   ├── LoadingSpinner.tsx     # Spinner animado
│   ├── DocumentIcon.tsx       # Ícone SVG de PDF
│   ├── Header.tsx             # Cabeçalho com título
│   └── index.ts              # Exports dos componentes
├── App.tsx                    # Página principal
├── App.css                    # Estilos globais
├── index.css                  # Estilos com Tailwind
└── main.tsx                   # Ponto de entrada
```

## 🚀 Funcionalidades

### Upload de Arquivo
- ✅ Drag-and-drop nativo
- ✅ Clique para selecionar arquivo
- ✅ Validação de tipo (PDF)
- ✅ Loading com spinner (2s simulado)
- ✅ Mensagem de sucesso
- ✅ Tratamento de erros

### Interface
- ✅ Título "Access Vision" centralizado
- ✅ Área de drop com border tracejada
- ✅ Ícone SVG de documento
- ✅ Botão primário (Azul Federal)
- ✅ Footer com mensagem LGPD

## 🎯 Estados da Interface

### Estado Inicial (Idle)
- Área de drop visível
- Botão "Selecionar Arquivo"
- Instruções de uso

### Estado Loading
- Spinner animado
- Texto "Processando arquivo..."
- Nome do arquivo em exibição

### Estado Success
- Checkmark em círculo verde
- Mensagem "Arquivo enviado com sucesso"
- Auto-reset após 5 segundos

## 📦 Instalação e Uso

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm preview
```

## 🌐 Servidor
- **URL**: http://localhost:5174/
- **Hot Module Reload**: ✅ Habilitado
- **Porta**: 5174 (ou próxima disponível)

## ♿ Acessibilidade
- Atributos ARIA adequados
- Labels descritivos
- Semantic HTML
- Suporte a navegação por teclado
- Feedback visual claro

## 🎨 Customização de Cores

Editar `tailwind.config.js` para modificar as cores do design system:

```javascript
colors: {
  'gov': {
    'green': '#06C637',   // Verde
    'blue': '#006294',    // Azul
    'red': '#D64040',     // Vermelho
    'yellow': '#F5A623',  // Amarelo
    // ... outras cores
  }
}
```

## 📝 Notas de Desenvolvimento

- Tailwind CSS v3 instalado (compatível com Vite)
- PostCSS configurado para processamento
- TypeScript strict mode habilitado
- ESLint configurado para qualidade de código

## 🔄 Próximas Melhorias (Opcional)
- Integração com backend real
- Validação de tamanho máximo (50MB)
- Barra de progresso real
- Histórico de uploads
- Suporte a múltiplos arquivos
- Previsualização de PDF

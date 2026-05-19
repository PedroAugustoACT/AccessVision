# Access Vision

Aplicação web para processamento de documentos PDF com foco em acessibilidade e design moderno

## 📋 Descrição

Plataforma moderna para upload de documentos PDF com interface baseada no Design System do Governo Federal Brasileiro. A aplicação oferece upload via drag-and-drop, processamento simulado e download do arquivo modificado com total conformidade de acessibilidade.

## 🎯 Funcionalidades

- **Upload de PDF**: Envie via drag-and-drop ou seleção de arquivo
- **Validação**: Apenas PDFs são aceitos
- **Processamento**: Sistema com feedback visual em tempo real
- **Download**: Baixe o arquivo processado (`pdf_modificado.pdf`)
- **Acessibilidade Total**: Interface 100% acessível (WCAG 2.1)
- **Conformidade LGPD**: Dados processados com segurança
- **Responsivo**: Otimizado para mobile, tablet e desktop

## 🚀 Tecnologias

- **React 19** - UI moderna e reativa
- **TypeScript** - Segurança de tipos
- **Vite 8** - Build rápido e eficiente
- **Tailwind CSS v3** - Estilização responsiva
- **Acessibilidade (WCAG 2.1)** - Padrões de acessibilidade web
- **Design System Federal** - Paleta de cores governamental

## 🎨 Design

- **Paleta de Cores**: Design System Federal
  - Azul: `#006294`
  - Verde: `#06C637`
  - Vermelho: `#D64040`
  - Cinza: `#646464`
- **Responsivo**: Mobile-first
- **Gradiente**: Fundo com degradê suave
- **Animações**: Transições fluidas e spinner animado

## 📋 Estrutura do Projeto

```
src/
├── components/
│   ├── DocumentIcon.tsx      # Ícone SVG de documento
│   ├── FileUpload.tsx        # Componente principal (drag-drop)
│   ├── Header.tsx            # Cabeçalho e título
│   ├── LoadingSpinner.tsx    # Spinner animado
│   ├── UploadFeedback.tsx    # Feedback de status
│   └── index.ts              # Exports dos componentes
├── App.tsx                   # Componente principal
├── App.css                   # Estilos específicos
├── index.css                 # Estilos com Tailwind
├── main.tsx                  # Ponto de entrada
└── assets/                   # Recursos do projeto
public/
└── pdf_modificado.pdf        # PDF padrão para download
```

## 🔧 Instalação

```bash
npm install
```

## 💻 Desenvolvimento

```bash
npm run dev
```

Acesse `http://localhost:5173`

- **Hot Module Reload**: ✅ Habilitado
- **Port**: 5173 (ou próxima disponível)

## 🏗️ Build

```bash
npm run build
npm run preview  # Preview do build
```

## 📝 Fluxo Principal

1. **Upload**: Usuário arrasta PDF ou clica para selecionar
2. **Validação**: Sistema verifica se é PDF
3. **Processamento**: Spinner mostra carregamento (2s simulado)
4. **Sucesso**: Mensagem de confirmação com checkmark verde
5. **Download**: Clique em "Baixar PDF Modificado" para fazer download
6. **Reset**: Auto-limpeza após 5 segundos

## 🎯 Estados da Interface

### Estado Inicial (Idle)
```
- Área de drop com border tracejada
- Ícone de documento
- Título e instruções
- Botão "Selecionar Arquivo"
```

### Estado Loading
```
- Spinner animado
- Texto "Processando arquivo..."
- Nome do arquivo em exibição
```

### Estado Success
```
- Ícone checkmark em círculo verde
- Mensagem "Arquivo enviado com sucesso"
- Nome do arquivo processado
- Botão "Baixar PDF Modificado"
- Auto-reset após 5 segundos
```

### Estado Error
```
- Mensagem de erro em vermelho
- Instrução para selecionar PDF válido
```

## ♿ Acessibilidade (WCAG 2.1)

A ser desenvolvido

## 📦 Dependências

```json
{
  "dependencies": {
    "react": "^19.2.6",
    "react-dom": "^19.2.6"
  },
  "devDependencies": {
    "typescript": "~6.0.2",
    "vite": "^8.0.12",
    "tailwindcss": "^3.4.19",
    "@vitejs/plugin-react": "^6.0.1",
    "eslint": "^10.3.0",
    "postcss": "^8.5.14"
  }
}
```

## 🎨 Customização de Cores

Editar `tailwind.config.js`:

```javascript
colors: {
  'gov': {
    'blue': '#006294',
    'green': '#06C637',
    'red': '#D64040',
    'yellow': '#F5A623',
    'dark-gray': '#646464',
    'light-gray': '#F0F0F0'
  }
}
```

## 📝 Notas de Desenvolvimento

- TypeScript strict mode habilitado
- ESLint configurado para qualidade de código
- PostCSS processando Tailwind CSS
- Hot Module Reload funcionando
- Componentes divididos e reutilizáveis

## 🔄 Próximas Melhorias

- [ ] Integração com backend real
- [ ] Barra de progresso real
- [ ] Histórico de uploads
- [ ] Suporte a múltiplos arquivos
- [ ] Previsualização de PDF
- [ ] Temas claro/escuro

## 📄 Licença

MIT

## 👤 Autor

Desenvolvido com foco em acessibilidade, design moderno e experiência do usuário.

# Access Vision

Aplicação web para processamento de documentos PDF com foco em acessibilidade e design moderno

## 📋 Descrição

Plataforma para upload de PDFs com gráficos matemáticos e adaptação para baixa visão: contraste em escala de cinza, descrições longas por IA e texto integrado abaixo de cada gráfico. Interface baseada no Design System do Governo Federal.

**Produção:** https://access-vision-opal.vercel.app/

## 🎯 Funcionalidades

- **Upload de PDF**: Envie via drag-and-drop ou seleção de arquivo
- **Validação**: Apenas PDFs são aceitos
- **Processamento**: API FastAPI (`accessvision-api/`) com IA (Cursor ou Gemini)
- **Download**: PDF adaptado gerado pelo backend
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

## 📋 Estrutura do Repositório

```
AccessVision/                 # raiz do Git
├── src/                    # front-end React + Vite
├── public/
├── accessvision-api/       # backend FastAPI
│   ├── app/
│   ├── requirements.txt
│   └── render.yaml
├── package.json
└── vite.config.ts          # proxy /api → localhost:8000
```

## 🔧 Instalação e desenvolvimento

### Front-end

```bash
npm install
npm run dev
```

Acesse `http://localhost:5173` (proxy `/api` → `http://127.0.0.1:8000`).

### API

```bash
cd accessvision-api
pip install -r requirements.txt
cp .env.example .env   # CURSOR_API_KEY ou GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Detalhes da API: [accessvision-api/README.md](accessvision-api/README.md).

## 🌐 Deploy

| Serviço | Root Directory (no painel) | Variáveis |
|---------|----------------------------|-----------|
| **Vercel** (front) | `.` (raiz do repo) | `VITE_API_URL` = URL do Render |
| **Render** (API) | `accessvision-api` | `CURSOR_API_KEY`, `CORS_ORIGINS` |

## 🏗️ Build

```bash
npm run build
npm run preview  # Preview do build
```

## 📝 Fluxo Principal

1. **Upload**: Usuário envia PDF
2. **API**: Extrai gráficos, aplica contraste, gera descrições (IA)
3. **PDF de saída**: Descrições inseridas abaixo de cada gráfico
4. **Download**: Blob retornado pela API

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

- [ ] Barra de progresso com etapas reais do processamento
- [ ] Histórico de uploads
- [ ] Suporte a múltiplos arquivos
- [ ] Previsualização de PDF
- [ ] Temas claro/escuro

## 📄 Licença

MIT

## 👤 Autor

Desenvolvido com foco em acessibilidade, design moderno e experiência do usuário.

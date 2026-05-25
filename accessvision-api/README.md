# AccessVision API

Backend FastAPI para processamento de PDFs com gráficos acessíveis.

## Endpoints

- `GET /health` — status
- `POST /api/v1/process` — upload PDF (`multipart/form-data`, campo `file`)

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `CURSOR_API_KEY` | Chave em [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations) |
| `CURSOR_MODEL_ID` | Modelo (padrão `composer-2`) |
| `LLM_PROVIDER` | `cursor` ou `gemini` |
| `GEMINI_API_KEY` | Alternativa gratuita com visão |
| `GEMINI_MODEL_ID` | Deve coincidir com o modelo do [painel de limites](https://aistudio.google.com/) (recomendado: `gemini-2.5-flash`) |
| `GEMINI_REQUEST_DELAY_SECONDS` | Pausa entre imagens (padrão `12` — tier gratuito ~5 RPM) |

**429 com quota “baixa” no painel:** as cotas são **por modelo**. Chamar `gemini-2.0-flash` enquanto o painel mostra `2.5-flash` pode retornar 429 na 1ª requisição (cota 0 para aquele modelo).

Em erro **429**, a API gera o PDF com descrições padrão e contraste aplicado.
| `CORS_ORIGINS` | Origens permitidas (incluir Vercel) |

Sem chave de IA, o sistema aplica contraste em escala de cinza e descrições placeholder.

## Teste offline (sem tokens de IA)

No `.env`:

```env
LLM_OFFLINE=true
GEMINI_API_KEY=
CURSOR_API_KEY=
```

Reinicie o `uvicorn`. O PDF ainda recebe contraste em escala de cinza, descrição placeholder e layout com texto abaixo do gráfico — **nenhuma chamada à API Gemini/Cursor**.

Alternativa equivalente: deixe `LLM_OFFLINE=false` e as duas chaves vazias.

## Verificar chave Gemini

```bash
cd accessvision-api
python scripts/verify_gemini.py
```

Se retornar `API Key not found`, gere uma nova chave (a antiga pode ter sido revogada).

## Desenvolvimento (a partir da raiz do repositório)

```bash
cd accessvision-api
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Na raiz do repo, `npm run dev` sobe o front; o Vite faz proxy de `/api` para a porta 8000.

## Deploy no Render

1. Conecte o repositório Git do AccessVision
2. **Root Directory:** `accessvision-api` (subpasta deste repo)
3. Adicione `CURSOR_API_KEY` em Environment
4. Confirme `CORS_ORIGINS` com `https://access-vision-opal.vercel.app`

## Vercel (front)

Em *Environment Variables*: `VITE_API_URL=https://<seu-app>.onrender.com` e redeploy.

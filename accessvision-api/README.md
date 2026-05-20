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
| `CORS_ORIGINS` | Origens permitidas (incluir Vercel) |

Sem chave de IA, o sistema aplica contraste em escala de cinza e descrições placeholder.

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

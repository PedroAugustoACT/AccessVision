import asyncio
import base64
import json
import logging

import httpx

from app.config import settings
from app.models import ExtractedImage
from app.services.image_utils import prepare_image_for_llm
from app.services.llm_base import DescriptionProvider, ImageProgressCallback

logger = logging.getLogger(__name__)

PROMPT = """Você é especialista em acessibilidade de gráficos educacionais (WCAG 1.1.1).
Descreva o gráfico na imagem em português com seções:
1 Tipo 2 Tema 3 Eixos 4 Tendência 5 Destaques 6 Conclusão.
Responda SOMENTE JSON: {"descricao_longa":"..."}"""

MAX_RETRIES = 3
RETRY_BASE_SECONDS = 15.0


def parse_gemini_error(resp: httpx.Response) -> str:
    try:
        body = resp.json()
        err = body.get("error", {})
        msg = err.get("message", resp.text[:400])
        status = err.get("status", "")
        return f"{status}: {msg}" if status else msg
    except Exception:
        return resp.text[:400] or f"HTTP {resp.status_code}"


class GeminiApiError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.status_code = status_code
        super().__init__(message)


class GeminiDescriptionProvider(DescriptionProvider):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        if len(settings.gemini_api_key.strip()) < 20:
            raise ValueError("GEMINI_API_KEY parece inválida (muito curta)")

    def _api_url(self) -> str:
        model = settings.gemini_model_id.strip()
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )

    async def describe_images(
        self,
        images: list[ExtractedImage],
        on_image_done: ImageProgressCallback | None = None,
    ) -> list[str]:
        results: list[str] = []
        total = len(images)
        delay = settings.gemini_request_delay_seconds
        logger.info("Gemini: modelo=%s, imagens=%s", settings.gemini_model_id, total)

        headers = {"Content-Type": "application/json"}
        params = {"key": settings.gemini_api_key}

        async with httpx.AsyncClient(timeout=120.0) as client:
            for index, img in enumerate(images):
                if index > 0 and delay > 0:
                    await asyncio.sleep(delay)

                jpeg_bytes, mime = prepare_image_for_llm(img.enhanced_bytes or img.raw_bytes)
                b64 = base64.b64encode(jpeg_bytes).decode("ascii")
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": PROMPT},
                                {"inline_data": {"mime_type": mime, "data": b64}},
                            ]
                        }
                    ],
                }
                text = await self._request_with_retry(client, payload, headers, params)
                cleaned = text.strip()
                start, end = cleaned.find("{"), cleaned.rfind("}")
                if start >= 0 and end > start:
                    data = json.loads(cleaned[start : end + 1])
                    results.append(data.get("descricao_longa", cleaned))
                else:
                    results.append(cleaned)

                if on_image_done:
                    await on_image_done(index + 1, total)

        return results

    async def _request_with_retry(
        self,
        client: httpx.AsyncClient,
        payload: dict,
        headers: dict,
        params: dict,
    ) -> str:
        last_detail = ""
        resp: httpx.Response | None = None

        for attempt in range(MAX_RETRIES):
            resp = await client.post(
                self._api_url(),
                json=payload,
                headers=headers,
                params=params,
            )
            if resp.status_code == 429:
                last_detail = parse_gemini_error(resp)
                logger.warning(
                    "Gemini 429 modelo=%s (tentativa %s/%s): %s",
                    settings.gemini_model_id,
                    attempt + 1,
                    MAX_RETRIES,
                    last_detail,
                )
                if "limit: 0" in last_detail.lower() or attempt == MAX_RETRIES - 1:
                    raise GeminiApiError(last_detail, 429)
                await asyncio.sleep(RETRY_BASE_SECONDS * (attempt + 1))
                continue

            if resp.is_error:
                last_detail = parse_gemini_error(resp)
                logger.error("Gemini %s: %s", resp.status_code, last_detail)
                if "API_KEY" in last_detail.upper() or "API key" in last_detail:
                    raise GeminiApiError(
                        "Chave Gemini inválida ou revogada. Crie uma nova em "
                        "https://aistudio.google.com/apikey e atualize o .env",
                        400,
                    )
                raise GeminiApiError(
                    f"Gemini ({settings.gemini_model_id}): {last_detail}",
                    resp.status_code,
                )

            try:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, json.JSONDecodeError) as exc:
                raise RuntimeError("Resposta inesperada da API Gemini") from exc

        raise GeminiApiError(last_detail or "Falha ao chamar Gemini", 500)

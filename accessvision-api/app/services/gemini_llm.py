import base64
import json
import re

import httpx

from app.config import settings
from app.models import ExtractedImage
from app.services.llm_base import DescriptionProvider

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

PROMPT = """Você é especialista em acessibilidade de gráficos educacionais (WCAG 1.1.1).
Descreva o gráfico na imagem em português com seções:
1 Tipo 2 Tema 3 Eixos 4 Tendência 5 Destaques 6 Conclusão.
Responda SOMENTE JSON: {"descricao_longa":"..."}"""


class GeminiDescriptionProvider(DescriptionProvider):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

    async def describe_images(self, images: list[ExtractedImage]) -> list[str]:
        results: list[str] = []
        async with httpx.AsyncClient(timeout=120.0) as client:
            for img in images:
                b64 = base64.b64encode(img.enhanced_bytes or img.raw_bytes).decode("ascii")
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": PROMPT},
                                {"inline_data": {"mime_type": "image/png", "data": b64}},
                            ]
                        }
                    ],
                }
                url = f"{GEMINI_URL}?key={settings.gemini_api_key}"
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                cleaned = text.strip()
                start, end = cleaned.find("{"), cleaned.rfind("}")
                if start >= 0 and end > start:
                    data = json.loads(cleaned[start : end + 1])
                    results.append(data.get("descricao_longa", cleaned))
                else:
                    results.append(cleaned)
        return results

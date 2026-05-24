import asyncio
import base64
import json
import re

import httpx

from app.config import settings
from app.models import ExtractedImage
from app.services.llm_base import DescriptionProvider, ImageProgressCallback

CURSOR_API = "https://api.cursor.com"
BATCH_SIZE = 5

PROMPT = """Você é especialista em acessibilidade de gráficos educacionais (WCAG 1.1.1).
Para cada imagem enviada (na ordem), produza descrição longa em português com:
1 Tipo do gráfico 2 Tema 3 Eixos 4 Tendência 5 Destaques 6 Conclusão.

Responda SOMENTE com JSON válido, sem markdown:
{"graficos":[{"indice":1,"descricao_longa":"..."}]}

O array deve ter exatamente {count} item(ns), índices de 1 a {count}."""


def _parse_descriptions(text: str, expected: int) -> list[str]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]
    data = json.loads(cleaned)
    graficos = data.get("graficos", [])
    out: list[str] = []
    for g in sorted(graficos, key=lambda x: x.get("indice", 0)):
        out.append(g.get("descricao_longa", "").strip())
    if len(out) < expected:
        out.extend([""] * (expected - len(out)))
    return out[:expected]


class CursorDescriptionProvider(DescriptionProvider):
    def __init__(self) -> None:
        if not settings.cursor_api_key:
            raise ValueError("CURSOR_API_KEY não configurada")

    async def describe_images(
        self,
        images: list[ExtractedImage],
        on_image_done: ImageProgressCallback | None = None,
    ) -> list[str]:
        if not images:
            return []
        total = len(images)
        descriptions: list[str] = []
        for offset in range(0, total, BATCH_SIZE):
            batch = images[offset : offset + BATCH_SIZE]
            batch_desc = await self._describe_batch(batch, offset)
            descriptions.extend(batch_desc)
            if on_image_done:
                await on_image_done(min(offset + len(batch), total), total)
        return descriptions

    async def _describe_batch(self, batch: list[ExtractedImage], offset: int) -> list[str]:
        images_b64 = [
            base64.b64encode(img.enhanced_bytes or img.raw_bytes).decode("ascii")
            for img in batch
        ]
        payload = {
            "prompt": {
                "text": PROMPT.format(count=len(batch)),
                "images": images_b64,
            },
            "model": {"id": settings.cursor_model_id},
        }
        auth = (settings.cursor_api_key, "")
        timeout = httpx.Timeout(settings.llm_timeout_seconds, connect=30.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{CURSOR_API}/v1/agents", auth=auth, json=payload)
            resp.raise_for_status()
            data = resp.json()
            agent_id = data["agent"]["id"]
            run_id = data["run"]["id"]
            text = await self._stream_assistant(client, auth, agent_id, run_id)
            try:
                return _parse_descriptions(text, len(batch))
            except (json.JSONDecodeError, KeyError):
                return [text.strip() if len(batch) == 1 else ""] * len(batch)

    async def _stream_assistant(
        self,
        client: httpx.AsyncClient,
        auth: tuple[str, str],
        agent_id: str,
        run_id: str,
    ) -> str:
        url = f"{CURSOR_API}/v1/agents/{agent_id}/runs/{run_id}/stream"
        parts: list[str] = []
        deadline = asyncio.get_event_loop().time() + settings.llm_timeout_seconds

        while asyncio.get_event_loop().time() < deadline:
            status_resp = await client.get(
                f"{CURSOR_API}/v1/agents/{agent_id}/runs/{run_id}",
                auth=auth,
            )
            if status_resp.status_code == 200:
                status = status_resp.json().get("status", "")
                if status in ("FINISHED", "FAILED", "CANCELLED", "ERROR"):
                    break
            await asyncio.sleep(2)

        async with client.stream("GET", url, auth=auth, headers={"Accept": "text/event-stream"}) as stream:
            event_type = ""
            async for line in stream.aiter_lines():
                if line.startswith("event:"):
                    event_type = line[6:].strip()
                elif line.startswith("data:") and event_type == "assistant":
                    try:
                        chunk = json.loads(line[5:].strip())
                        parts.append(chunk.get("text", ""))
                    except json.JSONDecodeError:
                        pass
                elif line.startswith("data:") and event_type == "result":
                    break

        if not parts:
            status_resp = await client.get(
                f"{CURSOR_API}/v1/agents/{agent_id}/runs/{run_id}",
                auth=auth,
            )
            status_resp.raise_for_status()
            if status_resp.json().get("status") == "FAILED":
                raise RuntimeError("Execução do agente Cursor falhou")

        return "".join(parts)

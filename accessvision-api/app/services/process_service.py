import logging
from typing import Awaitable, Callable

import httpx

from app.services.fallback_llm import FallbackDescriptionProvider
from app.services.gemini_llm import GeminiApiError
from app.services.image_enhancer import enhance_all
from app.services.llm_factory import get_description_provider
from app.services.pdf_builder import build_accessible_pdf
from app.services.pdf_extractor import extract_images

logger = logging.getLogger(__name__)

# Callback de progresso: (etapa, mensagem, porcentagem 0-100)
ProgressCallback = Callable[[str, str, int], Awaitable[None]]


async def _noop(*_: object) -> None:
    pass


async def _describe_with_fallback(
    images: list,
    on_image_done: Callable[[int, int], Awaitable[None]] | None = None,
) -> list[str]:
    provider = get_description_provider()
    try:
        return await provider.describe_images(images, on_image_done)
    except GeminiApiError as exc:
        if exc.status_code == 429:
            logger.warning("Gemini limite (429). PDF com descrições padrão.")
            return await FallbackDescriptionProvider().describe_images(images, on_image_done)
        raise
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            logger.warning("Limite de requisições da IA (429). PDF com descrições padrão.")
            return await FallbackDescriptionProvider().describe_images(images, on_image_done)
        raise
    except Exception as exc:
        logger.warning("Falha na IA (%s). Usando descrições padrão.", exc)
        return await FallbackDescriptionProvider().describe_images(images, on_image_done)


async def process_pdf(
    pdf_bytes: bytes,
    on_progress: ProgressCallback | None = None,
) -> tuple[bytes, int]:
    emit = on_progress or _noop

    await emit("extract", "Extraindo gráficos do PDF…", 5)
    doc, images = extract_images(pdf_bytes)
    n = len(images)

    if not images:
        await emit("done", "Nenhum gráfico encontrado — PDF retornado sem alterações", 100)
        return pdf_bytes, 0

    await emit("extract", f"{n} gráfico(s) identificado(s)", 15)

    await emit("enhance", "Aprimorando contraste e escala de cinza…", 20)
    enhance_all(images)
    await emit("enhance", "Contraste aplicado com sucesso", 30)

    await emit("describe", f"Iniciando descrição com IA (0 / {n})…", 32)

    async def on_image_done(done: int, total: int) -> None:
        pct = 32 + int(50 * done / total)
        await emit("describe", f"Gráfico {done} / {total} descrito", pct)

    descriptions = await _describe_with_fallback(images, on_image_done)

    for img, desc in zip(images, descriptions, strict=False):
        img.description = desc or ""

    await emit("build", "Construindo PDF acessível…", 85)
    result = build_accessible_pdf(doc, images)
    doc.close()

    await emit("done", f"{n} gráfico(s) adaptado(s) com sucesso", 100)
    return result, n

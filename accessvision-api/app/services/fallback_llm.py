from app.models import ExtractedImage
from app.services.llm_base import DescriptionProvider, ImageProgressCallback


class FallbackDescriptionProvider(DescriptionProvider):
    """Descrições genéricas quando nenhuma API de IA está configurada."""

    async def describe_images(
        self,
        images: list[ExtractedImage],
        on_image_done: ImageProgressCallback | None = None,
    ) -> list[str]:
        results: list[str] = []
        total = len(images)
        for img in images:
            results.append(
                f"[Modo offline] Gráfico {img.image_index + 1} (página {img.page_index + 1}). "
                "Descrição longa por IA desativada para testes sem consumo de tokens. "
                "O gráfico foi adaptado com escala de cinza e maior contraste. "
                "Ative a IA removendo LLM_OFFLINE no .env quando for usar em produção."
            )
            if on_image_done:
                await on_image_done(len(results), total)
        return results

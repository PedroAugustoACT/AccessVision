from app.models import ExtractedImage
from app.services.llm_base import DescriptionProvider


class FallbackDescriptionProvider(DescriptionProvider):
    """Descrições genéricas quando nenhuma API de IA está configurada."""

    async def describe_images(self, images: list[ExtractedImage]) -> list[str]:
        return [
            (
                f"Gráfico {img.image_index + 1} (página {img.page_index + 1}). "
                "Descrição automática não disponível: configure CURSOR_API_KEY ou GEMINI_API_KEY. "
                "Este material foi processado com melhoria de contraste em escala de cinza."
            )
            for img in images
        ]

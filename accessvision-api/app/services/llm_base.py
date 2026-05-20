import abc

from app.models import ExtractedImage


class DescriptionProvider(abc.ABC):
    @abc.abstractmethod
    async def describe_images(self, images: list[ExtractedImage]) -> list[str]:
        """Retorna uma descrição por imagem, na mesma ordem."""

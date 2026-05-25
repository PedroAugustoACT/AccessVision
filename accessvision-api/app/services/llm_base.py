import abc
from typing import Awaitable, Callable

from app.models import ExtractedImage

# Callback chamado após cada imagem descrita: (index_concluido, total)
ImageProgressCallback = Callable[[int, int], Awaitable[None]]


class DescriptionProvider(abc.ABC):
    @abc.abstractmethod
    async def describe_images(
        self,
        images: list[ExtractedImage],
        on_image_done: ImageProgressCallback | None = None,
    ) -> list[str]:
        """Retorna uma descrição por imagem, na mesma ordem."""

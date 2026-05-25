from app.config import settings
from app.services.cursor_llm import CursorDescriptionProvider
from app.services.fallback_llm import FallbackDescriptionProvider
from app.services.gemini_llm import GeminiDescriptionProvider
from app.services.llm_base import DescriptionProvider


def get_description_provider() -> DescriptionProvider:
    if settings.llm_offline:
        return FallbackDescriptionProvider()

    provider = settings.llm_provider.lower()
    if provider == "gemini" and settings.gemini_api_key:
        return GeminiDescriptionProvider()
    if settings.cursor_api_key:
        return CursorDescriptionProvider()
    if settings.gemini_api_key:
        return GeminiDescriptionProvider()
    return FallbackDescriptionProvider()

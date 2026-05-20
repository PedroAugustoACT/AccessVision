from app.models import ExtractedImage
from app.services.image_enhancer import enhance_all
from app.services.llm_factory import get_description_provider
from app.services.pdf_builder import build_accessible_pdf
from app.services.pdf_extractor import extract_images


async def process_pdf(pdf_bytes: bytes) -> tuple[bytes, int]:
    doc, images = extract_images(pdf_bytes)

    if not images:
        return pdf_bytes, 0

    enhance_all(images)

    provider = get_description_provider()
    descriptions = await provider.describe_images(images)
    for img, desc in zip(images, descriptions, strict=False):
        img.description = desc or ""

    result = build_accessible_pdf(doc, images)
    doc.close()
    return result, len(images)

import io

from PIL import Image, ImageEnhance, ImageOps

from app.models import ExtractedImage


def enhance_image(raw_bytes: bytes, contrast_factor: float = 1.8, scale: float = 1.0) -> bytes:
    img = Image.open(io.BytesIO(raw_bytes))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img = ImageOps.grayscale(img)
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)
    if scale != 1.0:
        w, h = img.size
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def enhance_all(images: list[ExtractedImage]) -> None:
    for item in images:
        item.enhanced_bytes = enhance_image(item.raw_bytes)

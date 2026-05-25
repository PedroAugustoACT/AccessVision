import io

from PIL import Image

MAX_LLM_SIDE = 1536
JPEG_QUALITY = 85


def prepare_image_for_llm(image_bytes: bytes) -> tuple[bytes, str]:
    """Normaliza imagem para JPEG e limita tamanho (evita 400 por MIME/payload)."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    w, h = img.size
    longest = max(w, h)
    if longest > MAX_LLM_SIDE:
        scale = MAX_LLM_SIDE / longest
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=JPEG_QUALITY)
    return out.getvalue(), "image/jpeg"

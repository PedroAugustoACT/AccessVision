import fitz

from app.models import ExtractedImage

MARGIN_BELOW = 10
PAGE_BOTTOM_MARGIN = 48
FONT_SIZE = 11
LABEL = "Descrição acessível do gráfico:\n"


def _replace_image_on_page(page: fitz.Page, bbox: fitz.Rect, image_bytes: bytes) -> None:
    try:
        page.insert_image(bbox, stream=image_bytes, keep_proportion=True, overlay=True)
    except Exception:
        pass


def _insert_description(
    doc: fitz.Document,
    page_index: int,
    bbox: fitz.Rect,
    description: str,
    page_num_human: int,
) -> None:
    page = doc[page_index]
    full_text = f"{LABEL}{description}"
    page_height = page.rect.height
    x0 = max(bbox.x0, 36)
    x1 = min(bbox.x1, page.rect.width - 36)
    if x1 <= x0:
        x0, x1 = 36, page.rect.width - 36

    y_top = bbox.y1 + MARGIN_BELOW
    y_bottom = page_height - PAGE_BOTTOM_MARGIN

    if y_bottom - y_top < 40:
        _insert_continuation_page(doc, page_index, page_num_human, full_text)
        return

    rect = fitz.Rect(x0, y_top, x1, y_bottom)
    overflow = page.insert_textbox(
        rect,
        full_text,
        fontsize=FONT_SIZE,
        fontname="helv",
        align=fitz.TEXT_ALIGN_LEFT,
    )

    if overflow is not None and str(overflow).strip():
        _insert_continuation_page(doc, page_index, page_num_human, full_text)


def _insert_continuation_page(
    doc: fitz.Document,
    after_page_index: int,
    page_num_human: int,
    text: str,
) -> None:
    ref_page = doc[after_page_index]
    new_page = doc.new_page(pno=after_page_index + 1, width=ref_page.rect.width, height=ref_page.rect.height)
    header = f"Descrição do gráfico (página {page_num_human})\n\n"
    rect = fitz.Rect(36, 48, new_page.rect.width - 36, new_page.rect.height - 48)
    new_page.insert_textbox(
        rect,
        header + text,
        fontsize=FONT_SIZE,
        fontname="helv",
    )


def build_accessible_pdf(doc: fitz.Document, images: list[ExtractedImage]) -> bytes:
    for img in images:
        if img.enhanced_bytes:
            page = doc[img.page_index]
            _replace_image_on_page(page, img.bbox, img.enhanced_bytes)

    by_page: dict[int, list[ExtractedImage]] = {}
    for img in images:
        by_page.setdefault(img.page_index, []).append(img)

    for page_index in sorted(by_page.keys(), reverse=True):
        for img in sorted(by_page[page_index], key=lambda i: i.bbox.y1, reverse=True):
            if img.description:
                _insert_description(
                    doc,
                    page_index,
                    img.bbox,
                    img.description,
                    img.page_index + 1,
                )

    return doc.tobytes(deflate=True, garbage=4)

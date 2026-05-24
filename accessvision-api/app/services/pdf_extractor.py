import fitz

from app.models import ExtractedImage

MIN_IMAGE_SIZE = 50


def extract_images(pdf_bytes: bytes) -> tuple[fitz.Document, list[ExtractedImage]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    by_key: dict[tuple[int, int], ExtractedImage] = {}
    global_index = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                continue
            if not rects:
                continue

            try:
                base = doc.extract_image(xref)
                raw = base["image"]
            except Exception:
                continue

            union = fitz.Rect()
            for bbox in rects:
                if bbox.width < MIN_IMAGE_SIZE or bbox.height < MIN_IMAGE_SIZE:
                    continue
                union |= bbox
            if union.is_empty:
                continue

            key = (page_index, xref)
            if key in by_key:
                by_key[key].bbox |= union
            else:
                by_key[key] = ExtractedImage(
                    page_index=page_index,
                    image_index=global_index,
                    xref=xref,
                    bbox=union,
                    raw_bytes=raw,
                )
                global_index += 1

    return doc, list(by_key.values())

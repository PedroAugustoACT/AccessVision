from dataclasses import dataclass

import fitz


@dataclass
class ExtractedImage:
    page_index: int
    image_index: int
    xref: int
    bbox: fitz.Rect
    raw_bytes: bytes
    enhanced_bytes: bytes | None = None
    description: str = ""

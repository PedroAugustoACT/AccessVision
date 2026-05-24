import logging

import fitz

from app.models import ExtractedImage

logger = logging.getLogger(__name__)

PAGE_MARGIN_X = 36
FONT_SIZE = 11
LABEL = "Descrição acessível do gráfico:\n"
MIN_DESC_HEIGHT = 48
CHART_X_PAD = 60
MIN_CHART_AREA = 80 * 80
QUESTION_MARKERS = ("a)", "b)", "c)", "d)", "Questão", "Descrição acessível")

# Limite máximo (em pontos PDF) abaixo do gráfico para incluir elementos
# relacionados (legenda, título do eixo, etc.) no "footprint".
# Evita que bordas ou grades verticais estendam o footprint até o fundo da página.
MAX_BELOW_CHART = 60

# Espaçamento vertical entre o footprint do gráfico e a caixa de descrição
DESC_GAP_ABOVE = 10
DESC_GAP_BELOW = 6


# ---------------------------------------------------------------------------
# Helpers de geometria
# ---------------------------------------------------------------------------


def _drawing_bbox(drawing: dict) -> fitz.Rect | None:
    rect = drawing.get("rect")
    if rect is not None:
        return fitz.Rect(rect)

    points: list[fitz.Point] = []
    for item in drawing.get("items", ()):
        if not item:
            continue
        op = item[0]
        if op == "re" and len(item) > 1:
            return fitz.Rect(item[1])
        if op in ("l", "c") and len(item) >= 3:
            points.append(fitz.Point(item[1]))
            points.append(fitz.Point(item[2]))
        elif op == "qu" and len(item) >= 5:
            for pt in item[1:5]:
                points.append(fitz.Point(pt))

    if not points:
        return None
    return fitz.Rect(points)


def _resolve_chart_rect(page: fitz.Page, xref: int, hint: fitz.Rect) -> fitz.Rect:
    """Retorna o retângulo da imagem do gráfico na página."""
    chart = fitz.Rect(hint)
    try:
        xref_rects = list(page.get_image_rects(xref))
        if xref_rects:
            chart = xref_rects[0]
            for r in xref_rects[1:]:
                chart |= r
    except Exception:
        pass

    largest = fitz.Rect(chart)
    largest_area = chart.get_area()

    for img in page.get_images(full=True):
        ix = img[0]
        try:
            rects = page.get_image_rects(ix)
        except Exception:
            continue
        for rect in rects:
            area = rect.get_area()
            if area < MIN_CHART_AREA:
                continue
            if area > largest_area:
                largest = fitz.Rect(rect)
                largest_area = area

    if largest_area > chart.get_area() * 1.05:
        logger.info(
            "Gráfico: usando maior imagem da página (area %.0f > hint %.0f)",
            largest_area,
            chart.get_area(),
        )
        return largest

    return chart


def _chart_footprint(page: fitz.Page, chart_rect: fitz.Rect) -> fitz.Rect:
    """
    Expande o retângulo do gráfico para incluir elementos diretamente
    relacionados (legenda de eixos, título inline, etc.) limitando a busca
    a MAX_BELOW_CHART pontos abaixo do gráfico.

    Ao limitar o band verticalmente evita-se que bordas ou grades longas
    empurrem foot.y1 para o fundo da página, o que causava a inserção da
    descrição fora do lugar.
    """
    foot = fitz.Rect(chart_rect)

    # Região de busca: horizontalmente ampliada, verticalmente limitada
    band = fitz.Rect(
        foot.x0 - CHART_X_PAD,
        foot.y0 - 15,
        foot.x1 + CHART_X_PAD,
        chart_rect.y1 + MAX_BELOW_CHART,  # ← limitado, não vai até o fundo da página
    )

    for drawing in page.get_drawings():
        dr = _drawing_bbox(drawing)
        if dr is None or dr.is_empty:
            continue
        if not dr.intersects(band):
            continue
        # Só incorpora se o drawing estiver majoritariamente dentro do band vertical
        if dr.y1 > band.y1:
            continue
        foot |= dr

    for block in page.get_text("blocks"):
        if len(block) < 5:
            continue
        text = str(block[4]).strip()
        if not text or any(text.startswith(m) for m in QUESTION_MARKERS):
            continue
        rect = fitz.Rect(block[:4])
        if not rect.intersects(band):
            continue
        if len(text) > 60:
            continue
        # Não incorpora textos que estejam claramente abaixo do gráfico
        if rect.y0 > chart_rect.y1 + MAX_BELOW_CHART:
            continue
        if rect.y0 >= chart_rect.y0 - 15 and rect.y1 <= chart_rect.y1 + MAX_BELOW_CHART:
            foot |= rect

    return foot


# ---------------------------------------------------------------------------
# Medição de texto
# ---------------------------------------------------------------------------


def _measure_text_height(text: str, text_width: float) -> float:
    doc = fitz.open()
    try:
        page = doc.new_page(width=text_width + 72, height=4000)
        rect = fitz.Rect(PAGE_MARGIN_X, 36, PAGE_MARGIN_X + text_width, 3900)
        page.insert_textbox(rect, text, fontsize=FONT_SIZE, fontname="helv")
        y_max = 36.0
        for block in page.get_text("blocks"):
            if len(block) >= 4:
                y_max = max(y_max, float(block[3]))
        return max(MIN_DESC_HEIGHT, (y_max - 36) + 24)
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Substituição de imagem no doc original
# ---------------------------------------------------------------------------


def _replace_image_on_page(page: fitz.Page, xref: int, image_bytes: bytes) -> None:
    try:
        page.replace_image(xref, stream=image_bytes)
    except Exception as exc:
        logger.warning("replace_image falhou xref=%s: %s", xref, exc)


# ---------------------------------------------------------------------------
# Reconstrução da página por strips (rasterizados + overlay de texto)
# ---------------------------------------------------------------------------

# Escala de renderização para os strips rasterizados.
# 2× = 144 DPI, suficiente para exibição em tela e impressão comum.
# Aumente para 3.0 se precisar de qualidade de impressão de alta definição.
RENDER_SCALE = 2.0


def _render_strip(
    page: fitz.Page, src_clip: fitz.Rect, dst_rect: fitz.Rect, new_page: fitz.Page
) -> None:
    """
    Rasteriza a região `src_clip` da `page` e insere como imagem em `new_page`.

    Usar get_pixmap em vez de show_pdf_page(clip=...) elimina o texto
    "fantasma": show_pdf_page aplica o clip apenas visualmente, mas o texto
    original permanece no Form XObject e pode ser extraído por leitores de
    tela ou ferramentas de busca. A rasterização converte tudo em pixels.
    O texto selecionável é restaurado separadamente por _reinsert_text_overlay.
    """
    mat = fitz.Matrix(RENDER_SCALE, RENDER_SCALE)
    pix = page.get_pixmap(matrix=mat, clip=src_clip, alpha=False)
    new_page.insert_image(dst_rect, pixmap=pix)


def _reinsert_text_overlay(
    src_page: fitz.Page,
    new_page: fitz.Page,
    src_clip: fitz.Rect,
    y_delta: float,
) -> None:
    """
    Re-insere como texto invisível (render_mode=3) todo o texto que estava no
    strip `src_clip` da página original, deslocado verticalmente por `y_delta`.

    Este padrão "OCR-style overlay" é o mesmo usado em PDFs gerados por OCR:
    a camada visual vem da imagem rasterizada; a camada de texto é invisível
    mas selecionável, copiável e lida por leitores de tela e indexadores.

    Apenas spans cujo ponto de origem (baseline) esteja dentro de `src_clip`
    são incluídos, evitando duplicação em bordas de corte.
    """
    try:
        # "dict" retorna spans com origin (baseline), size e text corretamente
        # decodificados para qualquer fonte embutida no PDF.
        # "rawdict" falha em decodificar texto quando o PDF usa mapeamentos de
        # encoding não-padrão, devolvendo text="" — por isso usamos "dict".
        text_dict = src_page.get_text(
            "dict",
            clip=src_clip,
            flags=fitz.TEXT_PRESERVE_WHITESPACE,
        )
    except Exception as exc:
        logger.warning("Falha ao extrair texto para overlay: %s", exc)
        return

    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:  # apenas blocos de texto (type 0)
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if not text:
                    continue
                origin = span.get("origin")
                if origin is None:
                    continue
                # Filtra pelo ponto de origem (baseline y) para evitar
                # duplicar texto que cruza a fronteira do clip
                if not (src_clip.y0 <= origin[1] <= src_clip.y1):
                    continue
                fontsize = max(4.0, float(span.get("size", FONT_SIZE)))
                new_origin = fitz.Point(origin[0], origin[1] + y_delta)
                try:
                    new_page.insert_text(
                        new_origin,
                        text,
                        fontsize=fontsize,
                        render_mode=3,  # invisível: selecionável mas sem renderização visual
                    )
                except Exception as exc:
                    logger.debug("Falha ao inserir texto overlay '%s': %s", text[:20], exc)


def _build_page_with_descriptions(
    out: fitz.Document,
    src: fitz.Document,
    page_index: int,
    page_images: list[ExtractedImage],
) -> None:
    """
    Cria uma nova página em `out` a partir de strips da página `page_index`
    de `src`, inserindo as descrições acessíveis entre os strips.

    Estratégia híbrida (visual raster + texto invisível + descrição visível):
    1. Calcula onde cada descrição deve ser inserida (abaixo do footprint
       do gráfico correspondente).
    2. Cria uma página mais alta em `out`.
    3. Para cada strip:
       a. Rasteriza a fatia → imagem sem texto fantasma (_render_strip)
       b. Re-insere o texto original como overlay invisível selecionável
          (_reinsert_text_overlay) no mesmo local, preservando seleção e
          cópia de texto, pesquisa e leitura por tecnologias assistivas.
    4. Insere a descrição acessível como texto visível na lacuna criada.
    """
    page = src[page_index]
    pw = page.rect.width
    ph = page.rect.height
    text_width = pw - 2 * PAGE_MARGIN_X

    # Monta lista de pontos de inserção ordenados de cima para baixo
    inserts: list[tuple[float, float, str]] = []
    for img in sorted(page_images, key=lambda i: i.bbox.y1):
        if not img.description:
            continue
        chart_rect = _resolve_chart_rect(page, img.xref, img.bbox)
        foot = _chart_footprint(page, chart_rect)
        full_text = f"{LABEL}{img.description}"
        desc_height = _measure_text_height(full_text, text_width)
        block_height = DESC_GAP_ABOVE + desc_height + DESC_GAP_BELOW
        inserts.append((foot.y1, block_height, full_text))
        logger.debug(
            "Página %d: inserção de legenda em y=%.1f, altura=%.1f",
            page_index,
            foot.y1,
            block_height,
        )

    if not inserts:
        # Nenhuma descrição: copia a página sem modificação
        out.insert_pdf(src, from_page=page_index, to_page=page_index)
        return

    total_extra = sum(bh for _, bh, _ in inserts)
    new_ph = ph + total_extra

    new_page = out.new_page(width=pw, height=new_ph)

    # Percorre os pontos de inserção, copiando strips e inserindo texto
    src_y = 0.0   # cursor na página original
    dst_y = 0.0   # cursor na nova página

    for y_insert, block_height, full_text in inserts:
        # Strip: de src_y até y_insert (rasterizado + overlay de texto)
        strip_h = y_insert - src_y
        if strip_h > 1:
            src_clip = fitz.Rect(0, src_y, pw, y_insert)
            dst_rect = fitz.Rect(0, dst_y, pw, dst_y + strip_h)
            y_delta = dst_y - src_y  # deslocamento a aplicar nas coordenadas de texto
            _render_strip(page, src_clip, dst_rect, new_page)
            _reinsert_text_overlay(page, new_page, src_clip, y_delta)
            dst_y += strip_h

        # Lacuna para a descrição (texto visível e pesquisável)
        y_text = dst_y + DESC_GAP_ABOVE
        desc_rect = fitz.Rect(
            PAGE_MARGIN_X,
            y_text,
            pw - PAGE_MARGIN_X,
            y_text + block_height - DESC_GAP_ABOVE - DESC_GAP_BELOW,
        )
        new_page.insert_textbox(
            desc_rect,
            full_text,
            fontsize=FONT_SIZE,
            fontname="helv",
            align=fitz.TEXT_ALIGN_LEFT,
        )
        dst_y += block_height
        src_y = y_insert

    # Strip final: tudo que restou abaixo do último ponto de inserção
    if ph - src_y > 1:
        src_clip = fitz.Rect(0, src_y, pw, ph)
        dst_rect = fitz.Rect(0, dst_y, pw, dst_y + (ph - src_y))
        y_delta = dst_y - src_y
        _render_strip(page, src_clip, dst_rect, new_page)
        _reinsert_text_overlay(page, new_page, src_clip, y_delta)


# ---------------------------------------------------------------------------
# Ponto de entrada público
# ---------------------------------------------------------------------------


def build_accessible_pdf(doc: fitz.Document, images: list[ExtractedImage]) -> bytes:
    by_page: dict[int, list[ExtractedImage]] = {}
    for img in images:
        by_page.setdefault(img.page_index, []).append(img)

    # 1) Aplica as imagens aprimoradas no doc original antes de reconstruir.
    #    Assim, os strips copiados via show_pdf_page já conterão a versão
    #    aprimorada do gráfico.
    for img in images:
        if img.enhanced_bytes:
            page = doc[img.page_index]
            _replace_image_on_page(page, img.xref, img.enhanced_bytes)

    # 2) Reconstrói cada página: copia as sem gráfico intactas, reconstrói
    #    as com gráfico inserindo a legenda entre strips.
    out = fitz.open()

    for page_index in range(len(doc)):
        page_imgs = by_page.get(page_index, [])
        has_desc = any(img.description for img in page_imgs)

        if not has_desc:
            out.insert_pdf(doc, from_page=page_index, to_page=page_index)
        else:
            _build_page_with_descriptions(out, doc, page_index, page_imgs)

    return out.tobytes(deflate=True, garbage=4)

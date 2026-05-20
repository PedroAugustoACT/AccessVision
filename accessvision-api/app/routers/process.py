from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.config import settings
from app.services.process_service import process_pdf

router = APIRouter(prefix="/api/v1", tags=["process"])

MAX_BYTES = settings.max_upload_mb * 1024 * 1024


@router.post("/process")
async def process_document(file: UploadFile = File(...)) -> Response:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF válido.")

    content_type = file.content_type or ""
    if "pdf" not in content_type.lower() and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser PDF.")

    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite de {settings.max_upload_mb} MB.",
        )
    if len(raw) < 100:
        raise HTTPException(status_code=400, detail="PDF vazio ou inválido.")

    try:
        result_bytes, graph_count = await process_pdf(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar PDF: {exc}",
        ) from exc

    base_name = file.filename.rsplit(".", 1)[0]
    out_name = f"acessivel_{base_name}.pdf"

    return Response(
        content=result_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{out_name}"',
            "X-Graphs-Processed": str(graph_count),
        },
    )

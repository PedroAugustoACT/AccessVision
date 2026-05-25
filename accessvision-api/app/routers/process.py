import asyncio
import base64
import json
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse

from app.config import settings
from app.services.process_service import process_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["process"])

MAX_BYTES = settings.max_upload_mb * 1024 * 1024

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # desativa buffer em proxies nginx (ex.: Render)
}


def _validate_upload(file: UploadFile, raw: bytes) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF válido.")
    content_type = file.content_type or ""
    if "pdf" not in content_type.lower() and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser PDF.")
    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite de {settings.max_upload_mb} MB.",
        )
    if len(raw) < 100:
        raise HTTPException(status_code=400, detail="PDF vazio ou inválido.")


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# Endpoint síncrono original (mantido para compatibilidade)
# ---------------------------------------------------------------------------


@router.post("/process")
async def process_document(file: UploadFile = File(...)) -> Response:
    raw = await file.read()
    _validate_upload(file, raw)

    try:
        result_bytes, graph_count = await process_pdf(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        from app.services.gemini_llm import GeminiApiError

        if isinstance(exc, GeminiApiError):
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar PDF: {exc}",
        ) from exc

    base_name = (file.filename or "documento").rsplit(".", 1)[0]
    out_name = f"acessivel_{base_name}.pdf"

    return Response(
        content=result_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{out_name}"',
            "X-Graphs-Processed": str(graph_count),
        },
    )


# ---------------------------------------------------------------------------
# Endpoint com progresso em tempo real via SSE
# ---------------------------------------------------------------------------


@router.post("/process/stream")
async def process_document_stream(file: UploadFile = File(...)) -> StreamingResponse:
    """
    Processa o PDF e emite eventos SSE com o progresso de cada etapa.

    Formato dos eventos:
      data: {"step": "extract"|"enhance"|"describe"|"build"|"done"|"error",
              "message": "...", "progress": 0-100}

    Evento final de sucesso inclui adicionalmente:
      "pdf_b64": "<base64 do PDF gerado>",
      "filename": "acessivel_<nome>.pdf",
      "count": <número de gráficos>
    """
    raw = await file.read()
    _validate_upload(file, raw)

    base_name = (file.filename or "documento").rsplit(".", 1)[0]
    out_name = f"acessivel_{base_name}.pdf"

    queue: asyncio.Queue[dict] = asyncio.Queue()

    async def on_progress(step: str, message: str, progress: int) -> None:
        await queue.put({"step": step, "message": message, "progress": progress})

    async def run_processing() -> None:
        try:
            result_bytes, count = await process_pdf(raw, on_progress)
            b64 = base64.b64encode(result_bytes).decode("ascii")
            await queue.put(
                {
                    "step": "result",
                    "message": f"{count} gráfico(s) adaptado(s) com sucesso",
                    "progress": 100,
                    "pdf_b64": b64,
                    "filename": out_name,
                    "count": count,
                }
            )
        except Exception as exc:
            logger.exception("Erro no processamento SSE")
            await queue.put(
                {
                    "step": "error",
                    "message": f"Erro ao processar PDF: {exc}",
                    "progress": 0,
                }
            )

    async def event_generator():
        task = asyncio.create_task(run_processing())
        try:
            while True:
                try:
                    # Aguarda até 15 s por um evento; se não chegar, envia
                    # um comentário SSE de keepalive para evitar que proxies
                    # (Render, Vercel, nginx) encerrem a conexão por inatividade.
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield _sse(event)
                if event["step"] in ("result", "error"):
                    break
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )

import asyncio
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.constants import ALLOWED_EXTENSIONS
from app.models.ingest import IngestResponse
from app.services import bm25_store
from app.services.chunker import chunk_document
from app.services.embedder import generate_embeddings
from app.services.vector_store import get_all_chunks, get_sources, store_chunks
from app.utils.document_loader import load_document

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    file_path = Path(file.filename or "")
    if file_path.suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}",
        )

    existing = {d["filename"] for d in get_sources()}
    if file_path.name in existing:
        return IngestResponse(
            filename=file.filename or "",
            chunks_created=0,
            message="Already ingested. Delete it first to re-ingest.",
        )

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=file_path.suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    named_path = tmp_path.rename(tmp_path.parent / file_path.name)

    # Offload blocking I/O and CPU work so the event loop stays free.
    text = await asyncio.to_thread(load_document, named_path)
    chunks = await asyncio.to_thread(chunk_document, text, named_path)
    embeddings = await asyncio.to_thread(generate_embeddings, [c.text for c in chunks])
    await asyncio.to_thread(store_chunks, chunks, embeddings)
    all_chunks = await asyncio.to_thread(get_all_chunks)
    await asyncio.to_thread(bm25_store.build_index, all_chunks)

    return IngestResponse(
        filename=file.filename or "",
        chunks_created=len(chunks),
        message="Document ingested successfully.",
    )

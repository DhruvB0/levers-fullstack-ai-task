import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.ingest import IngestResponse
from app.services.chunker import chunk_document
from app.services.embedder import generate_embeddings
from app.services.vector_store import store_chunks
from app.utils.document_loader import load_document

router = APIRouter()

ALLOWED_EXTENSIONS = {".md", ".csv"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    """Upload and ingest a document into the vector store."""
    file_path = Path(file.filename or "")
    if file_path.suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}",
        )

    with tempfile.NamedTemporaryFile(suffix=file_path.suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    # Rename temp file to preserve original filename for source tracking
    named_path = tmp_path.rename(tmp_path.parent / file_path.name)
    text = load_document(named_path)
    chunks = chunk_document(text, named_path)
    embeddings = generate_embeddings([chunk.text for chunk in chunks])
    store_chunks(chunks, embeddings)

    return IngestResponse(
        filename=file.filename or "",
        chunks_created=len(chunks),
        message="Document ingested successfully.",
    )

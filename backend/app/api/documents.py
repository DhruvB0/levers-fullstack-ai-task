from fastapi import APIRouter, HTTPException

from app.services import bm25_store
from app.services.vector_store import delete_by_source, get_all_chunks, get_sources

router = APIRouter()


@router.get("/documents")
async def list_documents() -> list[dict]:
    return get_sources()


@router.delete("/documents/{filename}")
async def delete_document(filename: str) -> dict:
    deleted = delete_by_source(filename)
    if deleted == 0:
        raise HTTPException(
            status_code=404, detail=f"Document '{filename}' not found."
        )
    bm25_store.build_index(get_all_chunks())
    return {
        "filename": filename,
        "chunks_deleted": deleted,
        "message": "Document deleted successfully.",
    }

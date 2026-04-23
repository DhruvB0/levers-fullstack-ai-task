import logging
from pathlib import Path

from app.core.config import get_settings
from app.services import bm25_store
from app.services.chunker import chunk_document
from app.services.embedder import generate_embeddings
from app.services.vector_store import get_all_chunks, get_document_count, store_chunks
from app.utils.document_loader import load_document

logger = logging.getLogger(__name__)
settings = get_settings()


def seed_reference_documents() -> None:
    """
    Ingest reference documents into ChromaDB on first startup.

    Checks count before ingesting so container restarts don't
    re-embed all documents and waste API credits.
    """
    if get_document_count() > 0:
        logger.info(
            "Vector store already seeded. Rebuilding BM25 index from existing corpus."
        )
        bm25_store.build_index(get_all_chunks())
        return

    seed_path = Path(settings.seed_data_path)
    files = list(seed_path.glob("*.md")) + list(seed_path.glob("*.csv"))

    if not files:
        logger.warning("No seed files found at %s", seed_path)
        return

    all_chunks = []
    for file_path in files:
        logger.info("Loading seed file: %s", file_path.name)
        text = load_document(file_path)
        chunks = chunk_document(text, file_path)
        all_chunks.extend(chunks)

    logger.info("Generating embeddings for %d chunks...", len(all_chunks))
    texts = [chunk.text for chunk in all_chunks]
    embeddings = generate_embeddings(texts)

    store_chunks(all_chunks, embeddings)
    bm25_store.build_index(get_all_chunks())
    logger.info("Seeded %d chunks from %d files.", len(all_chunks), len(files))

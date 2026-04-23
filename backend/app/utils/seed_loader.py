import logging
from pathlib import Path

from app.core.config import get_settings
from app.services import bm25_store
from app.services.chunker import chunk_document
from app.services.embedder import generate_embeddings
from app.services.vector_store import get_all_chunks, get_sources, store_chunks
from app.utils.document_loader import load_document

logger = logging.getLogger(__name__)
settings = get_settings()


def seed_reference_documents() -> None:
    seed_path = Path(settings.seed_data_path)
    files = list(seed_path.glob("*.md")) + list(seed_path.glob("*.csv"))

    if not files:
        logger.warning("No seed files found at %s", seed_path)
        bm25_store.build_index(get_all_chunks())
        return

    # Ingest any seed file not already in the store so deleted files are
    # restored on container restart without re-embedding files that exist.
    existing = {d["filename"] for d in get_sources()}
    missing = [f for f in files if f.name not in existing]

    if missing:
        all_chunks = []
        for file_path in missing:
            logger.info("Seeding missing file: %s", file_path.name)
            text = load_document(file_path)
            chunks = chunk_document(text, file_path)
            all_chunks.extend(chunks)

        logger.info("Generating embeddings for %d chunks...", len(all_chunks))
        embeddings = generate_embeddings([c.text for c in all_chunks])
        store_chunks(all_chunks, embeddings)
        logger.info("Seeded %d chunks from %d files.", len(all_chunks), len(missing))
    else:
        logger.info("All seed files present. Rebuilding BM25 index.")

    bm25_store.build_index(get_all_chunks())

import logging

import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI

from app.core.config import get_settings
from app.services.chunker import Chunk

logger = logging.getLogger(__name__)
settings = get_settings()

_client: ClientAPI | None = None
_collection: Collection | None = None


def _connect() -> Collection:
    global _client, _collection
    _client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    _collection = _client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def get_collection() -> Collection:
    global _collection
    if _collection is None:
        _connect()
    return _collection


def _run(fn):
    """Call fn(collection), reconnecting once on transient failure."""
    try:
        return fn(get_collection())
    except Exception:
        logger.warning("ChromaDB call failed — reconnecting and retrying.")
        _connect()
        return fn(get_collection())


def store_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    _run(lambda c: c.upsert(
        ids=[f"{chunk.source}_{chunk.chunk_index}" for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk.text for chunk in chunks],
        metadatas=[{"source": chunk.source} for chunk in chunks],
    ))


def retrieve_similar_chunks(query_embedding: list[float], top_k: int) -> list[dict]:
    results = _run(lambda c: c.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    ))
    return [
        {"text": doc, "source": meta["source"]}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def get_document_count() -> int:
    return _run(lambda c: c.count())


def get_sources() -> list[dict]:
    result = _run(lambda c: c.get(include=["metadatas"]))
    counts: dict[str, int] = {}
    for meta in result["metadatas"]:
        src = meta["source"]
        counts[src] = counts.get(src, 0) + 1
    return [{"filename": k, "chunk_count": v} for k, v in sorted(counts.items())]


def delete_by_source(source: str) -> int:
    result = _run(lambda c: c.get(where={"source": source}))
    ids = result["ids"]
    if ids:
        _run(lambda c: c.delete(ids=ids))
    return len(ids)


def get_all_chunks() -> list[dict]:
    result = _run(lambda c: c.get(include=["documents", "metadatas"]))
    return [
        {"text": doc, "source": meta["source"]}
        for doc, meta in zip(result["documents"], result["metadatas"])
    ]

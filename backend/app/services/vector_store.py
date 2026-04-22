import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI

from app.core.config import get_settings
from app.services.chunker import Chunk

settings = get_settings()

_client: ClientAPI | None = None
_collection: Collection | None = None


def get_collection() -> Collection:
    """
    Return the ChromaDB collection, creating it if needed.

    Module-level singleton — one HTTP client is sufficient and
    avoids the overhead of a new connection per request.
    """
    global _client, _collection
    if _collection is None:
        _client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        _collection = _client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def store_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    collection = get_collection()
    collection.upsert(
        ids=[f"{chunk.source}_{chunk.chunk_index}" for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk.text for chunk in chunks],
        metadatas=[{"source": chunk.source} for chunk in chunks],
    )


def retrieve_similar_chunks(
    query_embedding: list[float],
    top_k: int,
) -> list[dict]:
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {"text": doc, "source": meta["source"]}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def get_document_count() -> int:
    return get_collection().count()

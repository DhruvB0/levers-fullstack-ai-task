import hashlib
import logging

from app.core.config import get_settings
from app.services import bm25_store
from app.services.embedder import generate_single_embedding
from app.services.vector_store import retrieve_similar_chunks

logger = logging.getLogger(__name__)
settings = get_settings()

_SEP = "\n\n---\n\n"


def _reciprocal_rank_fusion(ranked_lists: list[list[dict]], k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            # Full-text hash avoids false deduplication from the 80-char prefix approach.
            key = hashlib.sha1(
                f"{item['source']}\x00{item['text']}".encode(), usedforsecurity=False
            ).hexdigest()
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            docs[key] = item
    return [docs[k] for k in sorted(scores, key=lambda x: scores[x], reverse=True)]


def get_relevant_context(query: str) -> tuple[str, list[str]]:
    corpus_size = bm25_store.get_index_size()
    if corpus_size == 0:
        return "", []

    # Cap fetch_k at corpus size to avoid ChromaDB raising on n_results > count.
    fetch_k = min(settings.top_k_results * 2, corpus_size)

    query_embedding = generate_single_embedding(query)
    vector_results = retrieve_similar_chunks(query_embedding, top_k=fetch_k)
    bm25_results = bm25_store.query_bm25(query, top_k=fetch_k)

    fused = _reciprocal_rank_fusion([vector_results, bm25_results])
    top_chunks = fused[: settings.top_k_results]

    if not top_chunks:
        return "", []

    context_parts: list[str] = []
    sources: list[str] = []
    total_chars = 0

    for chunk in top_chunks:
        part = f"[Source: {chunk['source']}]\n{chunk['text']}"
        if total_chars + len(part) > settings.max_context_chars:
            logger.warning("Context limit reached at %d chars; dropping remaining chunks.", total_chars)
            break
        context_parts.append(part)
        total_chars += len(part) + len(_SEP)
        if chunk["source"] not in sources:
            sources.append(chunk["source"])

    return _SEP.join(context_parts), sources

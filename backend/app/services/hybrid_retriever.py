from app.core.config import get_settings
from app.services import bm25_store
from app.services.embedder import generate_single_embedding
from app.services.vector_store import retrieve_similar_chunks

settings = get_settings()


def _reciprocal_rank_fusion(
    ranked_lists: list[list[dict]], k: int = 60
) -> list[dict]:
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            key = f"{item['source']}::{item['text'][:80]}"
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            docs[key] = item
    return [docs[k] for k in sorted(scores, key=lambda x: scores[x], reverse=True)]


def get_relevant_context(query: str) -> tuple[str, list[str]]:
    fetch_k = settings.top_k_results * 2

    query_embedding = generate_single_embedding(query)
    vector_results = retrieve_similar_chunks(query_embedding, top_k=fetch_k)
    bm25_results = bm25_store.query_bm25(query, top_k=fetch_k)

    fused = _reciprocal_rank_fusion([vector_results, bm25_results])
    top_chunks = fused[: settings.top_k_results]

    if not top_chunks:
        return "", []

    context_parts: list[str] = []
    sources: list[str] = []

    for chunk in top_chunks:
        context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
        if chunk["source"] not in sources:
            sources.append(chunk["source"])

    return "\n\n---\n\n".join(context_parts), sources

from app.core.config import get_settings
from app.services.embedder import generate_single_embedding
from app.services.vector_store import retrieve_similar_chunks

settings = get_settings()


def get_relevant_context(query: str) -> tuple[str, list[str]]:
    query_embedding = generate_single_embedding(query)
    chunks = retrieve_similar_chunks(query_embedding, top_k=settings.top_k_results)

    if not chunks:
        return "", []

    context_parts = []
    sources: list[str] = []

    for chunk in chunks:
        context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
        if chunk["source"] not in sources:
            sources.append(chunk["source"])

    return "\n\n---\n\n".join(context_parts), sources

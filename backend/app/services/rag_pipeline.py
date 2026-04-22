from collections.abc import Generator

from app.core.prompt_store import get_system_prompt
from app.services.llm import get_completion, stream_completion
from app.services.retriever import get_relevant_context
from app.services.vector_store import get_document_count

_EMPTY_STORE_MSG = (
    "No documents have been ingested yet. The knowledge base is empty."
)


def answer_query(query: str, model: str) -> dict:
    if get_document_count() == 0:
        return {"answer": _EMPTY_STORE_MSG, "sources": [], "rag_used": False}

    context, sources = get_relevant_context(query)
    system_prompt = get_system_prompt()
    answer = get_completion(system_prompt, context, query, model)

    return {"answer": answer, "sources": sources, "rag_used": True}


def stream_answer_query(query: str, model: str) -> Generator[str, None, None]:
    if get_document_count() == 0:
        yield _EMPTY_STORE_MSG
        return

    context, _ = get_relevant_context(query)
    system_prompt = get_system_prompt()

    yield from stream_completion(system_prompt, context, query, model)

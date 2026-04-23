from collections.abc import Generator

from app.core.config import get_settings
from app.core.constants import THINKING_MODELS
from app.services.openai_client import get_client

settings = get_settings()


def _build_messages(
    system_prompt: str,
    context: str,
    query: str,
    model: str,
) -> list[dict]:
    user_content = f"Context from documents:\n{context}\n\nQuestion: {query}"

    if model in THINKING_MODELS:
        return [{"role": "user", "content": f"{system_prompt}\n\n{user_content}"}]

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def get_completion(
    system_prompt: str,
    context: str,
    query: str,
    model: str,
) -> str:
    messages = _build_messages(system_prompt, context, query, model)
    kwargs: dict = {"model": model, "messages": messages}
    # Reasoning models (o1/o3) consume tokens for internal chain-of-thought;
    # capping at 1000 leaves nothing for the actual response — let them self-limit.
    if model not in THINKING_MODELS:
        kwargs["max_completion_tokens"] = settings.max_completion_tokens
    response = get_client().chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def stream_completion(
    system_prompt: str,
    context: str,
    query: str,
    model: str,
) -> Generator[str, None, None]:
    """
    Yield response tokens for SSE streaming.

    o1/o3 models don't support streaming — fall back to a single chunk
    so the caller doesn't need to handle the distinction.
    """
    if model in THINKING_MODELS:
        yield get_completion(system_prompt, context, query, model)
        return

    messages = _build_messages(system_prompt, context, query, model)
    stream = get_client().chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=settings.max_completion_tokens,
        stream=True,
    )
    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token

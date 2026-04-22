from collections.abc import Generator

from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

# o1 models reject the 'system' role — prompt must be injected as first user message
O1_MODELS = {"o1-mini", "o1-preview", "o1"}


def _build_messages(
    system_prompt: str,
    context: str,
    query: str,
    model: str,
) -> list[dict]:
    user_content = f"Context from documents:\n{context}\n\nQuestion: {query}"

    if model in O1_MODELS:
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
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=1000,
    )
    return response.choices[0].message.content or ""


def stream_completion(
    system_prompt: str,
    context: str,
    query: str,
    model: str,
) -> Generator[str, None, None]:
    """
    Yield response tokens for SSE streaming.

    o1 models don't support streaming — fall back to a single chunk
    so the caller doesn't need to handle the distinction.
    """
    if model in O1_MODELS:
        yield get_completion(system_prompt, context, query, model)
        return

    messages = _build_messages(system_prompt, context, query, model)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=1000,
        stream=True,
    )
    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token

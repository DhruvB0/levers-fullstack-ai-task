from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts in a single API call.

    Batching avoids rate limits. OpenAI's endpoint accepts up to 2048
    inputs per request — our ~30 chunks are handled in one call.
    """
    response = client.embeddings.create(
        input=texts,
        model=settings.embedding_model,
    )
    return [item.embedding for item in response.data]


def generate_single_embedding(text: str) -> list[float]:
    return generate_embeddings([text])[0]

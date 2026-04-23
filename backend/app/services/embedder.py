from app.core.config import get_settings
from app.services.openai_client import get_client

settings = get_settings()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    # Batching avoids rate limits. OpenAI accepts up to 2048 inputs per request.
    response = get_client().embeddings.create(
        input=texts,
        model=settings.embedding_model,
    )
    return [item.embedding for item in response.data]


def generate_single_embedding(text: str) -> list[float]:
    return generate_embeddings([text])[0]

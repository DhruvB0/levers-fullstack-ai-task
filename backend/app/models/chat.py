from pydantic import BaseModel

ALLOWED_MODELS = {"gpt-4o-mini", "o1-mini"}


class ChatRequest(BaseModel):
    query: str
    model: str = "gpt-4o-mini"
    stream: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What are the permitted calling hours?",
                "model": "gpt-4o-mini",
                "stream": False,
            }
        }
    }


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    rag_used: bool

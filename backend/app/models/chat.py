from pydantic import BaseModel, field_validator

from app.core.constants import ALLOWED_MODELS


class ChatRequest(BaseModel):
    query: str
    model: str = "gpt-4o-mini"
    stream: bool = False

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if v not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of {sorted(ALLOWED_MODELS)}")
        return v

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

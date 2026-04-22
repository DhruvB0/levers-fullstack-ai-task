from pydantic import BaseModel


class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    message: str

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import answer_query, stream_answer_query

router = APIRouter()


@router.post("/chat", response_model=None)
async def chat(request: ChatRequest) -> ChatResponse | StreamingResponse:
    """
    Main chat endpoint.

    If stream=True returns an SSE stream; otherwise returns full JSON.
    """
    if request.stream:

        def event_stream():
            for token in stream_answer_query(request.query, request.model):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no"},
        )

    result = answer_query(request.query, request.model)
    return ChatResponse(**result)

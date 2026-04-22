import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, config, ingest
from app.utils.seed_loader import seed_reference_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_reference_documents()
    yield


app = FastAPI(
    title="Debt Collection Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)
    logger.info(
        "request_id=%s method=%s path=%s status=%d latency=%dms",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


app.include_router(chat.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(config.router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.prompt_store import (
    get_system_prompt,
    reset_system_prompt,
    set_system_prompt,
)

router = APIRouter()


class SystemPromptResponse(BaseModel):
    system_prompt: str


class SystemPromptUpdate(BaseModel):
    system_prompt: str


@router.get("/config/system-prompt", response_model=SystemPromptResponse)
async def get_prompt() -> SystemPromptResponse:
    return SystemPromptResponse(system_prompt=get_system_prompt())


@router.put("/config/system-prompt", response_model=SystemPromptResponse)
async def update_prompt(body: SystemPromptUpdate) -> SystemPromptResponse:
    set_system_prompt(body.system_prompt)
    return SystemPromptResponse(system_prompt=get_system_prompt())


@router.delete("/config/system-prompt", response_model=SystemPromptResponse)
async def reset_prompt() -> SystemPromptResponse:
    reset_system_prompt()
    return SystemPromptResponse(system_prompt=get_system_prompt())

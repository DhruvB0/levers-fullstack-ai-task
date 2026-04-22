_DEFAULT_SYSTEM_PROMPT = (
    "You are a compliance assistant for debt collection agents. "
    "Answer questions using ONLY the provided context from company documents. "
    "If the context does not contain the answer, say so — "
    "do not make up information.\n\n"
    "When answering, cite which document the information came from. "
    "Be concise, professional, and accurate. "
    "If a question involves a specific account, provide the relevant details "
    "from the account data."
)

_system_prompt: str = _DEFAULT_SYSTEM_PROMPT


def get_system_prompt() -> str:
    return _system_prompt


def set_system_prompt(new_prompt: str) -> None:
    global _system_prompt
    _system_prompt = new_prompt


def reset_system_prompt() -> None:
    global _system_prompt
    _system_prompt = _DEFAULT_SYSTEM_PROMPT

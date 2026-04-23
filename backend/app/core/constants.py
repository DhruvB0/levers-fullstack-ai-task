# Reject 'system' role and don't support streaming — must be handled differently in llm.py.
THINKING_MODELS: frozenset[str] = frozenset({"o1-mini", "o1-preview", "o1", "o3-mini"})

ALLOWED_MODELS: frozenset[str] = frozenset({"gpt-4o-mini", "o1-mini", "o3-mini"})

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".md", ".csv"})

# These files use ## headers / markdown tables that must not be split mid-block.
SECTION_CHUNKED_FILENAMES: frozenset[str] = frozenset({"glossary.md"})

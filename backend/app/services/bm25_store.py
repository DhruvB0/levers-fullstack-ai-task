import logging
import re
import threading

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_index: BM25Okapi | None = None
_corpus: list[dict] = []


# Words that carry zero retrieval signal in a debt collection context.
# Intentionally minimal — when in doubt, keep the word.
# Do NOT add: not, no, may, must, should, will, cannot, never
# Those carry legal meaning and affect BM25 scoring correctly.
_STOP_WORDS = frozenset(
    {
        # articles
        "a",
        "an",
        "the",
        # basic prepositions
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        # pronouns
        "i",
        "me",
        "my",
        "we",
        "our",
        "you",
        "your",
        "it",
        "its",
        # question words
        "what",
        "which",
        "who",
        "whom",
        "how",
        # basic verbs
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "do",
        "does",
        "did",
        "have",
        "has",
        "had",
        # connectors
        "and",
        "or",
        "but",
        "so",
        "as",
        "than",
        "that",
        "this",
        # fillers
        "there",
        "here",
        "just",
        "also",
        "about",
    }
)


def _tokenize(text: str) -> list[str]:
    # Strip punctuation so "ACC-007?" → ["acc", "007"].
    # Filter stop words so common query terms don't drown out specific IDs.
    return [t for t in re.findall(r'\w+', text.lower()) if t not in _STOP_WORDS]


def build_index(corpus: list[dict]) -> None:
    global _index, _corpus
    tokenized = [_tokenize(item["text"]) for item in corpus]
    with _lock:
        _corpus = corpus
        _index = BM25Okapi(tokenized) if tokenized else None
    logger.info("BM25 index rebuilt with %d chunks.", len(corpus))


def query_bm25(query: str, top_k: int) -> list[dict]:
    with _lock:
        if _index is None or not _corpus:
            return []
        corpus_snapshot = _corpus
        scores = _index.get_scores(_tokenize(query))

    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [corpus_snapshot[i] for i in ranked[:top_k]]


def get_index_size() -> int:
    with _lock:
        return len(_corpus)

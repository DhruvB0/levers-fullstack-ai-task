import logging
import re
import threading

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_index: BM25Okapi | None = None
_corpus: list[dict] = []


def _tokenize(text: str) -> list[str]:
    # Strip punctuation before splitting so "ACC-007?" and "ACC-007" both
    # become ["acc", "007"] and match each other in BM25 scoring.
    return re.findall(r'\w+', text.lower())


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

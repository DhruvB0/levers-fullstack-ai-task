from unittest.mock import patch

from app.services.bm25_store import build_index, get_index_size, query_bm25
from app.services.hybrid_retriever import _reciprocal_rank_fusion, get_relevant_context

# ---------------------------------------------------------------------------
# _reciprocal_rank_fusion
# ---------------------------------------------------------------------------

def test_rrf_single_list_preserves_order():
    ranked = [
        {"text": "first", "source": "a.md"},
        {"text": "second", "source": "a.md"},
    ]
    result = _reciprocal_rank_fusion([ranked])
    assert result[0]["text"] == "first"
    assert result[1]["text"] == "second"


def test_rrf_identical_doc_in_both_lists_ranks_higher():
    shared = {"text": "shared chunk", "source": "a.md"}
    only_in_b = {"text": "unique", "source": "b.md"}
    list_a = [shared]
    list_b = [shared, only_in_b]
    result = _reciprocal_rank_fusion([list_a, list_b])
    assert result[0]["text"] == "shared chunk", "doc in both lists should rank first"


def test_rrf_interleaves_disjoint_results():
    list_a = [{"text": "chunk A", "source": "a.md"}]
    list_b = [{"text": "chunk B", "source": "b.md"}]
    result = _reciprocal_rank_fusion([list_a, list_b])
    texts = [r["text"] for r in result]
    assert "chunk A" in texts
    assert "chunk B" in texts


def test_rrf_empty_lists_returns_empty():
    assert _reciprocal_rank_fusion([[], []]) == []


def test_rrf_one_empty_list_returns_other():
    items = [{"text": "only", "source": "x.md"}]
    result = _reciprocal_rank_fusion([items, []])
    assert len(result) == 1
    assert result[0]["text"] == "only"


def test_rrf_deduplicates_identical_chunks():
    chunk = {"text": "duplicate", "source": "a.md"}
    result = _reciprocal_rank_fusion([[chunk], [chunk]])
    assert len(result) == 1


# ---------------------------------------------------------------------------
# bm25_store
# ---------------------------------------------------------------------------

def test_bm25_build_and_query():
    corpus = [
        {"text": "the quick brown fox jumps", "source": "a.md"},
        {"text": "lazy dog sitting in the sun", "source": "b.md"},
    ]
    build_index(corpus)
    results = query_bm25("quick fox", top_k=2)
    assert results[0]["source"] == "a.md"


def test_bm25_empty_corpus_returns_empty():
    build_index([])
    assert query_bm25("anything", top_k=5) == []


def test_bm25_get_index_size():
    corpus = [{"text": f"chunk {i}", "source": "a.md"} for i in range(5)]
    build_index(corpus)
    assert get_index_size() == 5


def test_bm25_top_k_limits_results():
    corpus = [{"text": f"keyword term {i}", "source": "a.md"} for i in range(10)]
    build_index(corpus)
    results = query_bm25("keyword term", top_k=3)
    assert len(results) <= 3


# ---------------------------------------------------------------------------
# get_relevant_context integration (mocked deps)
# ---------------------------------------------------------------------------

@patch("app.services.hybrid_retriever.bm25_store.query_bm25")
@patch("app.services.hybrid_retriever.retrieve_similar_chunks")
@patch("app.services.hybrid_retriever.generate_single_embedding")
def test_get_relevant_context_combines_both(mock_embed, mock_vector, mock_bm25):
    mock_embed.return_value = [0.1] * 10
    mock_vector.return_value = [{"text": "vector result", "source": "v.md"}]
    mock_bm25.return_value = [{"text": "bm25 result", "source": "b.md"}]

    context, sources = get_relevant_context("test query")

    assert "vector result" in context or "bm25 result" in context
    assert len(sources) >= 1


@patch("app.services.hybrid_retriever.bm25_store.query_bm25")
@patch("app.services.hybrid_retriever.retrieve_similar_chunks")
@patch("app.services.hybrid_retriever.generate_single_embedding")
def test_get_relevant_context_empty_bm25_falls_back_to_vector(
    mock_embed, mock_vector, mock_bm25
):
    mock_embed.return_value = [0.1] * 10
    mock_vector.return_value = [{"text": "only vector", "source": "v.md"}]
    mock_bm25.return_value = []

    context, sources = get_relevant_context("test query")

    assert "only vector" in context
    assert sources == ["v.md"]


@patch("app.services.hybrid_retriever.bm25_store.query_bm25")
@patch("app.services.hybrid_retriever.retrieve_similar_chunks")
@patch("app.services.hybrid_retriever.generate_single_embedding")
def test_get_relevant_context_both_empty_returns_empty(
    mock_embed, mock_vector, mock_bm25
):
    mock_embed.return_value = [0.1] * 10
    mock_vector.return_value = []
    mock_bm25.return_value = []

    context, sources = get_relevant_context("test query")

    assert context == ""
    assert sources == []

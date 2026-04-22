from pathlib import Path

from app.services.chunker import chunk_by_fixed_size, chunk_by_section, chunk_document


def test_fixed_size_chunker_produces_multiple_chunks():
    text = " ".join(["word"] * 1000)
    chunks = chunk_by_fixed_size(text, "test.md", chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_fixed_size_chunker_respects_chunk_size():
    text = " ".join(["word"] * 1000)
    chunks = chunk_by_fixed_size(text, "test.md", chunk_size=500, overlap=50)
    assert all(len(c.text.split()) <= 500 for c in chunks)


def test_overlap_exists_between_adjacent_chunks():
    text = " ".join(str(i) for i in range(600))
    chunks = chunk_by_fixed_size(text, "test.md", chunk_size=500, overlap=50)
    last_words = set(chunks[0].text.split()[-50:])
    first_words = set(chunks[1].text.split()[:50])
    assert last_words & first_words


def test_chunk_source_and_index_are_set():
    text = " ".join(["word"] * 600)
    chunks = chunk_by_fixed_size(text, "source.md", chunk_size=500, overlap=50)
    assert chunks[0].source == "source.md"
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_section_chunker_keeps_table_rows_intact():
    table = "## Status Table\n| A | B |\n|---|---|\n| val1 | val2 |"
    text = f"{table}\n\n## Next\nSome text"
    chunks = chunk_by_section(text, "glossary.md")
    assert any("val1" in c.text and "val2" in c.text for c in chunks)


def test_section_chunker_splits_on_headers():
    text = "## Section One\ncontent one\n## Section Two\ncontent two"
    chunks = chunk_by_section(text, "glossary.md")
    assert len(chunks) == 2


def test_glossary_uses_section_chunking():
    text = "## Section One\nsome content\n## Section Two\nmore content"
    chunks = chunk_document(text, Path("glossary.md"))
    assert len(chunks) == 2


def test_non_glossary_uses_fixed_chunking():
    text = " ".join(["word"] * 600)
    chunks = chunk_document(text, Path("fdcpa_quick_reference.md"))
    assert len(chunks) > 1


def test_empty_sections_are_filtered():
    text = "## Section One\n\n## Section Two\nactual content"
    chunks = chunk_by_section(text, "glossary.md")
    assert all(c.text.strip() for c in chunks)

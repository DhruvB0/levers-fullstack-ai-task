from dataclasses import dataclass
from pathlib import Path

from app.core.constants import SECTION_CHUNKED_FILENAMES


@dataclass
class Chunk:
    text: str
    source: str
    chunk_index: int


def chunk_by_fixed_size(
    text: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """
    Word-based fixed-size chunking with overlap.

    Word count is a close-enough approximation to tokens for our doc
    sizes and keeps the chunker dependency-free. Overlap prevents
    sentences split across boundaries from being missed entirely.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_text = " ".join(words[start:end])
        chunks.append(Chunk(text=chunk_text, source=source, chunk_index=len(chunks)))
        start += chunk_size - overlap

    return chunks


def chunk_by_section(text: str, source: str) -> list[Chunk]:
    """
    Split markdown by ## headers to keep sections intact.

    The glossary contains markdown tables. Fixed-size chunking can
    split a table mid-row, making it unreadable. Section-based chunking
    keeps each ## block as one unit.
    """
    sections: list[str] = []
    current_header = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append(current_header + "\n" + "\n".join(current_lines))
            current_header = line
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append(current_header + "\n" + "\n".join(current_lines))

    return [
        Chunk(text=section.strip(), source=source, chunk_index=i)
        for i, section in enumerate(sections)
        if section.strip()
    ]


def chunk_by_csv_rows(text: str, source: str) -> list[Chunk]:
    """
    One chunk per CSV row (already converted to prose paragraphs by load_csv_as_prose).

    load_csv_as_prose joins rows with '\n\n', so splitting on that separator
    recovers one self-contained prose description per account row.
    This prevents unrelated rows from being bundled into the same chunk and
    pulled together into context when only one account is relevant.
    """
    rows = [r.strip() for r in text.split("\n\n") if r.strip()]
    return [Chunk(text=row, source=source, chunk_index=i) for i, row in enumerate(rows)]


def chunk_document(text: str, file_path: Path) -> list[Chunk]:
    """
    Route to the correct chunking strategy based on file type.

    glossary.md  → section-based  (tables must not be split mid-row)
    *.csv        → one chunk per row (avoids mixing unrelated accounts in context)
    everything else → fixed-size
    """
    source = file_path.name

    if file_path.name in SECTION_CHUNKED_FILENAMES:
        return chunk_by_section(text, source)

    if file_path.suffix == ".csv":
        return chunk_by_csv_rows(text, source)

    return chunk_by_fixed_size(text, source)

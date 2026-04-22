"""CLI script to test the RAG pipeline end-to-end without the API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_pipeline import answer_query  # noqa: E402


def main() -> None:
    default_query = "What are the permitted calling hours?"
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else default_query
    print(f"Query: {query}\n")
    result = answer_query(query, model="gpt-4o-mini")
    print(f"Answer: {result['answer']}\n")
    print(f"Sources: {result['sources']}")
    print(f"RAG used: {result['rag_used']}")


if __name__ == "__main__":
    main()

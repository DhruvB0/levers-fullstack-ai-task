import csv
from pathlib import Path


def load_markdown(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def load_csv_as_prose(file_path: Path) -> str:
    # Prose gives embeddings semantic shape —
    # raw CSV column values have poor vector representation.
    paragraphs = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            paragraph = (
                f"Account {row['account_id']} belongs to {row['consumer_name']}. "
                f"Original creditor: {row['original_creditor']}. "
                f"Current balance: ${row['current_balance']}. "
                f"Status: {row['status']}. "
                f"Dispute status: {row['dispute_status']}. "
                f"State: {row['state']}. "
                f"Debt type: {row['debt_type']}. "
                f"Days delinquent: {row['days_delinquent']}. "
                f"Notes: {row['notes']}."
            )
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def load_document(file_path: Path) -> str:
    if file_path.suffix == ".md":
        return load_markdown(file_path)
    if file_path.suffix == ".csv":
        return load_csv_as_prose(file_path)
    raise ValueError(f"Unsupported file type: {file_path.suffix}")

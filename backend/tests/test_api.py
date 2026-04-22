from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_system_prompt_returns_default():
    response = client.get("/api/config/system-prompt")
    assert response.status_code == 200
    data = response.json()
    assert "system_prompt" in data
    assert len(data["system_prompt"]) > 0


def test_update_system_prompt():
    new_prompt = "You are a test assistant."
    response = client.put(
        "/api/config/system-prompt",
        json={"system_prompt": new_prompt},
    )
    assert response.status_code == 200
    assert response.json()["system_prompt"] == new_prompt


def test_reset_system_prompt():
    client.put("/api/config/system-prompt", json={"system_prompt": "changed"})
    response = client.delete("/api/config/system-prompt")
    assert response.status_code == 200
    # Should contain the default prompt keywords
    assert "compliance" in response.json()["system_prompt"].lower()


def test_chat_returns_response_structure():
    with patch("app.api.chat.answer_query") as mock_answer:
        mock_answer.return_value = {
            "answer": "Permitted hours are 8 AM to 9 PM.",
            "sources": ["fdcpa_quick_reference.md"],
            "rag_used": True,
        }
        response = client.post(
            "/api/chat",
            json={"query": "What are calling hours?", "model": "gpt-4o-mini"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "rag_used" in data


def test_empty_store_returns_warning():
    with (
        patch("app.services.vector_store.get_document_count", return_value=0),
        patch("app.services.rag_pipeline.get_document_count", return_value=0),
    ):
        response = client.post(
            "/api/chat",
            json={"query": "Any question", "model": "gpt-4o-mini", "stream": False},
        )
    assert response.status_code == 200
    assert "empty" in response.json()["answer"].lower()


def test_ingest_rejects_unsupported_extension():
    response = client.post(
        "/api/ingest",
        files={"file": ("test.pdf", b"pdf content", "application/pdf")},
    )
    assert response.status_code == 400


def test_chat_missing_query_returns_422():
    response = client.post(
        "/api/chat",
        json={"model": "gpt-4o-mini"},
    )
    assert response.status_code == 422

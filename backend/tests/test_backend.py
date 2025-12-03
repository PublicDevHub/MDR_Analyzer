import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.rag import retrieve_context
from backend.main import app
from httpx import AsyncClient, ASGITransport
import json

# Helper for async iteration
class MockAsyncIterator:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        self.iter = iter(self.items)
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

@pytest.mark.asyncio
async def test_retrieve_context():
    # Mock data
    mock_results = [
        {
            "reference_id": "1",
            "title": "Test Doc",
            "filename": "test.pdf",
            "content": "This is a test content."
        }
    ]

    # Mock embedding response
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

    # Patch the clients in backend.rag
    with patch("backend.rag.openai_client.embeddings.create", new_callable=AsyncMock) as mock_embed, \
         patch("backend.rag.search_client.search", new_callable=AsyncMock) as mock_search:

        mock_embed.return_value = mock_embedding_response
        mock_search.return_value = MockAsyncIterator(mock_results)

        sources, context = await retrieve_context("test query")

        assert len(sources) == 1
        assert sources[0].filename == "test.pdf"
        assert "This is a test content" in context

@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    # Mock retrieve_context and generate_answer

    # Mock generator for answer
    async def mock_answer_generator(*args, **kwargs):
        tokens = ["Hello", " world"]
        for t in tokens:
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = t
            yield chunk

    with patch("backend.main.retrieve_context", new_callable=AsyncMock) as mock_retrieve, \
         patch("backend.main.generate_answer", side_effect=mock_answer_generator) as mock_generate:

        mock_retrieve.return_value = (
            [{"reference_id": "1", "title": "A", "filename": "a.pdf"}],
            "Context"
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat/stream", json={"query": "hello"})

        assert response.status_code == 200
        lines = response.text.strip().split("\n")

        # Expect at least 3 lines: 1 for sources, 2 for tokens
        assert len(lines) >= 3

        # Check first line (Sources)
        sources_data = json.loads(lines[0])
        assert "sources" in sources_data
        assert sources_data["sources"][0]["filename"] == "a.pdf"

        # Check subsequent lines (Tokens)
        token_data_1 = json.loads(lines[1])
        assert token_data_1["token"] == "Hello"

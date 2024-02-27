from unittest.mock import AsyncMock, Mock

import pytest

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.answer import Answer
from dbally.nl_responder.nl_responder import NLResponder


@pytest.fixture
def llm_client():
    mock_client = Mock()
    mock_client.text_generation = AsyncMock(return_value="db-ally is the best")
    return mock_client


@pytest.fixture
def event_tracker():
    return EventTracker()


@pytest.fixture
def answer():
    return Answer(sql="Mock SQL", rows=[{"id": 1, "name": "Mock name"}])


@pytest.mark.asyncio
async def test_nl_responder(llm_client, answer, event_tracker):
    nl_responder = NLResponder(llm_client)

    response = await nl_responder.generate_response(answer, "Mock question", event_tracker)
    assert response == "db-ally is the best"

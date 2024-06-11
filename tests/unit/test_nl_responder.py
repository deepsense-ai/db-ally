from unittest.mock import AsyncMock

import pytest

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.nl_responder.nl_responder import NLResponder
from tests.unit.mocks import MockLLM


@pytest.fixture
def llm() -> MockLLM:
    llm = MockLLM()
    llm.client.call = AsyncMock(return_value="db-ally is the best")
    return llm


@pytest.fixture
def event_tracker() -> EventTracker:
    return EventTracker()


@pytest.fixture
def answer() -> ViewExecutionResult:
    return ViewExecutionResult(results=[{"id": 1, "name": "Mock name"}], context={"sql": "Mock SQL"})


@pytest.mark.asyncio
async def test_nl_responder(llm: MockLLM, answer: ViewExecutionResult, event_tracker: EventTracker):
    nl_responder = NLResponder(llm)
    response = await nl_responder.generate_response(answer, "Mock question", event_tracker)
    assert response == "db-ally is the best"

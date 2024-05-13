from dataclasses import dataclass
from unittest.mock import ANY, AsyncMock, Mock, call

import pytest

from dbally import create_collection
from dbally.llm_client.base import LLMClient, LLMOptions
from tests.unit.mocks import MockViewBase


class MockView1(MockViewBase):
    ...


class MockView2(MockViewBase):
    ...


@dataclass
class MockLLMOptions(LLMOptions):
    mock_property: int


class MockLLMClient(LLMClient[MockLLMOptions]):
    # TODO: Start calling super().__init__ and remove the pyling comment below
    # as soon as the base class is refactored to not have PromptBuilder initialization
    # hardcoded in its constructor.
    # See: DBALLY-105
    # pylint: disable=super-init-not-called
    def __init__(self, default_options: MockLLMOptions) -> None:
        self.model_name = "gpt-4"
        self.default_options = default_options
        self._prompt_builder = Mock()

    async def call(self, *_, **__) -> str:
        ...


@pytest.mark.asyncio
async def test_llm_options_propagation():
    default_options = MockLLMOptions(mock_property=1)
    custom_options = MockLLMOptions(mock_property=2)
    llm_client = MockLLMClient(default_options=default_options)

    collection = create_collection(
        name="test_collection",
        llm_client=llm_client,
    )

    collection.add(MockView1)
    collection.add(MockView2)

    collection.n_retries = 0
    collection._llm_client.call = AsyncMock(return_value="MockView1")

    await collection.ask(
        question="Mock question",
        return_natural_response=True,
        llm_options=custom_options,
    )

    assert llm_client.call.call_count == 3

    llm_client.call.assert_has_calls(
        [
            call(
                prompt=ANY,
                response_format=ANY,
                event=ANY,
                options=custom_options,
            ),
            call(
                prompt=ANY,
                response_format=ANY,
                event=ANY,
                options=custom_options,
            ),
            call(
                prompt=ANY,
                response_format=ANY,
                event=ANY,
                options=custom_options,
            ),
        ]
    )

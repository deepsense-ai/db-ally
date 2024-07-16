from unittest.mock import ANY, AsyncMock, call, patch

import pytest

from dbally import create_collection
from tests.unit.mocks import MockLLM, MockLLMOptions
from tests.unit.test_collection import MockView1, MockView2


@pytest.mark.asyncio
async def test_llm_options_propagation():
    default_options = MockLLMOptions(mock_property1=1, mock_property2="default mock")
    custom_options = MockLLMOptions(mock_property1=2)
    expected_options = MockLLMOptions(mock_property1=2, mock_property2="default mock")

    llm = MockLLM(default_options=default_options)
    llm.client.call = AsyncMock(return_value="MockView1")

    collection = create_collection(
        name="test_collection",
        llm=llm,
    )
    collection.n_retries = 0
    collection.add(MockView1)
    collection.add(MockView2)

    with patch("dbally.iql.IQLQuery.parse", AsyncMock()):
        await collection.ask(
            question="Mock question",
            return_natural_response=True,
            llm_options=custom_options,
        )

    assert llm.client.call.call_count == 3

    llm.client.call.assert_has_calls(
        [
            call(
                conversation=ANY,
                json_mode=ANY,
                event=ANY,
                options=expected_options,
            ),
            call(
                conversation=ANY,
                json_mode=ANY,
                event=ANY,
                options=expected_options,
            ),
            call(
                conversation=ANY,
                json_mode=ANY,
                event=ANY,
                options=expected_options,
            ),
        ]
    )

from typing import List
from unittest.mock import ANY, AsyncMock, call, patch

import pytest

from dbally import create_collection
from dbally.views.exposed_functions import ExposedFunction
from tests.unit.mocks import MockLLM, MockLLMOptions, MockViewBase
from tests.unit.test_collection import MockView1


class MockViewWithFilterAndAggregation(MockViewBase):
    """
    Mock view with an example filter and aggregation.
    """

    def list_filters(self) -> List[ExposedFunction]:
        return [ExposedFunction("test_filter", "", [])]

    def list_aggregations(self) -> List[ExposedFunction]:
        return [ExposedFunction("test_aggregation", "", [])]


@pytest.mark.asyncio
async def test_llm_options_propagation():
    default_options = MockLLMOptions(mock_property1=1, mock_property2="default mock")
    custom_options = MockLLMOptions(mock_property1=2)
    expected_options = MockLLMOptions(mock_property1=2, mock_property2="default mock")

    llm = MockLLM(default_options=default_options)
    llm.client.call = AsyncMock(return_value="MockViewWithFilterAndAggregation")

    collection = create_collection(
        name="test_collection",
        llm=llm,
    )
    collection.n_retries = 0
    collection.add(MockView1)
    collection.add(MockViewWithFilterAndAggregation)

    with patch("dbally.iql.IQLQuery.parse", AsyncMock()):
        await collection.ask(
            question="Mock question",
            return_natural_response=True,
            llm_options=custom_options,
        )

    assert llm.client.call.call_count == 4

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

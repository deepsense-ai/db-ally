import json
from collections import namedtuple
from typing import List
from unittest.mock import AsyncMock, Mock

import pytest
from openai.types.beta.threads.required_action_function_tool_call import Function, RequiredActionFunctionToolCall

from dbally.assistants.base import FunctionCallingError, FunctionCallState
from dbally.assistants.openai import _DBALLY_INFO, _DBALLY_INSTRUCTION, OpenAIAdapter, OpenAIDballyResponse
from dbally.iql_generator.prompt import UnsupportedQueryError

MOCK_VIEWS = {"view1": "description1", "view2": "description2"}
F_ID = "f_id"


@pytest.fixture
def openai_adapter() -> OpenAIAdapter:
    collection = AsyncMock()
    collection.list = Mock(return_value=MOCK_VIEWS)
    return OpenAIAdapter(collection)


@pytest.fixture
def tool_calls() -> List[RequiredActionFunctionToolCall]:
    call = RequiredActionFunctionToolCall(
        id=F_ID, function=Function(name="use_dbally", arguments='{"query": "mock query"}'), type="function"
    )

    return [call]


def test_generate_instruction(openai_adapter):
    k = list(MOCK_VIEWS.keys())
    v = list(MOCK_VIEWS.values())
    GT_INSTRUCTION = _DBALLY_INFO + f"{k[0]}: {v[0]}\n{k[1]}: {v[1]}\n" + _DBALLY_INSTRUCTION
    assert openai_adapter.generate_instruction() == GT_INSTRUCTION


@pytest.mark.asyncio
@pytest.mark.parametrize("n_calls", [1, 3])
async def test_process_response_no_query(n_calls, openai_adapter):
    call = RequiredActionFunctionToolCall(
        id=F_ID, function=Function(name="use_dbally", arguments="{}"), type="function"
    )
    tool_calls = [call] * n_calls

    response = await openai_adapter.process_response(tool_calls)
    state = FunctionCallState.INVALID_ARGUMENTS
    assert response == [OpenAIDballyResponse(F_ID, state, str(state))] * n_calls


@pytest.mark.asyncio
async def test_process_response_no_query_exception(openai_adapter):
    call = RequiredActionFunctionToolCall(
        id=F_ID, function=Function(name="use_dbally", arguments="{}"), type="function"
    )
    tool_calls = [call]

    with pytest.raises(FunctionCallingError) as excinfo:
        await openai_adapter.process_response(tool_calls, raise_exception=True)

    assert excinfo.value.state == FunctionCallState.INVALID_ARGUMENTS


@pytest.mark.asyncio
async def test_process_response_correct(openai_adapter, tool_calls):
    Response = namedtuple("Response", ["results"])
    MOCK_RESULT = Response("mock_results")
    openai_adapter.collection.ask = AsyncMock(return_value=MOCK_RESULT)

    response = await openai_adapter.process_response(tool_calls)
    assert response == [OpenAIDballyResponse(F_ID, FunctionCallState.SUCCESS, json.dumps(MOCK_RESULT.results))]


@pytest.mark.asyncio
async def test_process_response_unsupported(openai_adapter, tool_calls):
    openai_adapter.collection.ask = AsyncMock(side_effect=UnsupportedQueryError())

    response = await openai_adapter.process_response(tool_calls)
    state = FunctionCallState.UNSUPPORTED_QUERY
    assert response == [OpenAIDballyResponse(F_ID, state, str(state))]


@pytest.mark.asyncio
async def test_process_response_unsupported_exception(openai_adapter, tool_calls):
    openai_adapter.collection.ask = AsyncMock(side_effect=UnsupportedQueryError())

    with pytest.raises(FunctionCallingError) as excinfo:
        await openai_adapter.process_response(tool_calls, raise_exception=True)
    assert excinfo.value.state == FunctionCallState.UNSUPPORTED_QUERY


@pytest.mark.asyncio
async def test_process_response_invalid_json(openai_adapter):
    call = RequiredActionFunctionToolCall(
        id=F_ID, function=Function(name="use_dbally", arguments="{invalid_json"), type="function"
    )
    tool_calls = [call]
    response = await openai_adapter.process_response(tool_calls)
    state = FunctionCallState.INVALID_JSON
    assert response[0].state == state


def test_process_functions_execution(openai_adapter):
    response = [OpenAIDballyResponse(F_ID, FunctionCallState.SUCCESS, "mock_results")]
    assert openai_adapter.process_functions_execution(response) == [{"tool_call_id": F_ID, "output": "mock_results"}]

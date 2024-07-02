import json
from dataclasses import dataclass
from typing import Dict, List

from openai.types.beta.threads import RequiredActionFunctionToolCall

from dbally.assistants.base import AssistantAdapter, FunctionCallingError, FunctionCallState
from dbally.collection import Collection
from dbally.iql_generator.prompt import UnsupportedQueryError

_DBALLY_INFO = "Dbally has access to the following database views: "

_DBALLY_INSTRUCTION = (
    "Please ask questions in natural language e.g 'How many candidates have applied for the position of xyz'. "
    "If query can be divided into multiple parts, please use multiple function calls."
    "If necessary paraphrase queries and fill them with context information"
)


@dataclass
class OpenAIDballyResponse:
    """Dataclass to represent the response from the Dbally engine given the OpenAI function call request."""

    tool_call_id: str
    state: FunctionCallState
    output: str


class OpenAIAdapter(AssistantAdapter):
    """The AssistantsAdapter for the OpenAI API. To be used with OpenAI function calling or assistants API."""

    def __init__(self, collection: Collection, function_name: str = "use_dbally"):
        self.collection = collection
        self.dbally_description = self.generate_instruction()
        self.function_name = function_name

    def generate_instruction(self) -> str:
        """Generates instructions for GPT, on when to use dbally.

        Returns:
            str: Instruction that should be provided to the Assistants or function
            calling, so that GPT knows when to use dbally
        """
        function_description = _DBALLY_INFO

        for view_name, desc in self.collection.list().items():
            function_description += f"{view_name}: {desc}\n"

        function_description += _DBALLY_INSTRUCTION

        return function_description

    def generate_function_json(self) -> Dict:
        """Returns the definition of the function in JSON format, which is compliant with the OpenAI API.

        Returns:
            Dict: JSON definition of the function, with the description inferred from the provided Collection."""

        function_def = {
            "type": "function",
            "function": {
                "name": self.function_name,
                "description": self.dbally_description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query for the dbally engine",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
        return function_def

    async def process_response(
        self, tool_calls: List[RequiredActionFunctionToolCall], raise_exception: bool = False
    ) -> List[OpenAIDballyResponse]:
        """Process the response from the OpenAI API, and return the dbally output.

        Args:
            tool_calls (List[RequiredActionFunctionToolCall]): The tool calls returned by the OpenAI API
            raise_exception (bool): Whether to raise an exception if an error occurs during function execution

        Returns:
            List[OpenAIDballyResponse]: The output from the dbally engine.
            List will be empty if dbally was not in tool_calls.

        Raises:
            FunctionCallingError: If an error occurs during function execution and `raise_exception` flag is set to True
        """
        functions_execution = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            if function_name == self.function_name:
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    state = FunctionCallState.INVALID_JSON
                    response = f"Info: {str(state)} Error: {str(e)}"
                    function_args = None

                if function_args is not None:
                    if "query" not in function_args:
                        state = FunctionCallState.INVALID_ARGUMENTS
                        response = str(state)
                    else:
                        try:
                            state = FunctionCallState.SUCCESS
                            # TODO: Think about placing it inside gather. Use case with more than
                            # 1 call to dbally is probably rather rare though
                            # In case of  raise_exception use TaskGroup, otherwise asyncio.gather.
                            response_dbally = await self.collection.ask(question=function_args.get("query"))
                            response = json.dumps(response_dbally.results)
                        except UnsupportedQueryError:
                            state = FunctionCallState.UNSUPPORTED_QUERY
                            response = str(state)

                if raise_exception and state != FunctionCallState.SUCCESS:
                    raise FunctionCallingError(
                        state, f"Function {function_name} execution failed with state: {response}"
                    )

                functions_execution.append(
                    OpenAIDballyResponse(tool_call_id=tool_call.id, state=state, output=response)
                )

        return functions_execution

    def process_functions_execution(self, functions_executions: List[OpenAIDballyResponse]) -> List[Dict[str, str]]:
        """Processes result of `process_response` to a format compliant with OpenAI Assistants API.

        Args:
            functions_executions (List[OpenAIDballyResponse]): result of `process_response`

        Returns:
            List[Dict[str, str]]: The output from the dbally engine in a format compliant with OpenAI Assistants API
        """
        parsed_functions_execution = []

        for f_exec in functions_executions:
            parsed_functions_execution.append(
                {
                    "tool_call_id": f_exec.tool_call_id,
                    "output": f_exec.output,
                }
            )

        return parsed_functions_execution

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List

from dbally.exceptions import DbAllyError


class FunctionCallState(Enum):
    """Enum to represent the state of the Assistants function call."""

    SUCCESS = auto()
    INVALID_ARGUMENTS = auto()
    UNSUPPORTED_QUERY = auto()
    INVALID_JSON = auto()

    def __str__(self) -> str:
        """Returns the string representation of the FunctionCallState. Used to give feedback to the LLM agent."""
        return {
            FunctionCallState.SUCCESS: "Success: The query was successfully processed by the dbally",
            FunctionCallState.INVALID_ARGUMENTS: "ValueError: 'query' argument is required for the dballye",
            FunctionCallState.UNSUPPORTED_QUERY: "UnsupportedQueryError: The query is not supported by the dbally",
            FunctionCallState.INVALID_JSON: (
                "ValueError: The JSON containing arguments for the function" "call could not be parsed with json.loads"
            ),
        }[self]


class FunctionCallingError(DbAllyError):
    """Exception raised when an error occurs during Assistants function call function."""

    def __init__(self, state: FunctionCallState, msg: str) -> None:
        super().__init__(msg)
        self.state = state


class AssistantAdapter(ABC):
    """This Interface is used to support dbally as a tool for Assistants API or
    function calling. It is inspired by OpenAI function calling API, where user defines a
    JSON definition of the function, and the LLM select when the function should be called.

    The general idea is that we need to:
    1. Create a custom instruction, describing when the Assistant should use dbally.
    2. Generate a function JSON, compliant with provider API, describing how to use dbally.
    3. Process the response from the Assistant, and return the dbally output.
    """

    @abstractmethod
    def generate_instruction(
        self,
    ) -> str:
        """This function should generate the instruction for the LLM, on when to use dbally.
        Different LLMs may require different prompts for it.

        Returns:
            str: Instruction that should be provided to the LLM, so that it knows when to use dbally
        """

    @abstractmethod
    def generate_function_json(
        self,
    ) -> Dict:
        """Returns the definition of the function in JSON format. This JSON should be compliant with the provider API
        and contain all the necessary information to execute the function correctly.

        Returns:
            Dict: JSON definition of the function
        """

    @abstractmethod
    async def process_response(self, tool_calls: List[Any], raise_exception: bool = False) -> List[Any]:
        """Process the response from the LLM, and return the dbally output. LLMs don't execute functions by themselves,
        but set themselves in requires_action states, and then users need to execute functions by themselves.

        Args:
            tool_calls (List[Any]): The tool calls returned by the LLM
            raise_exception (bool): Whether to raise an exception if an error occurs during function execution

        Returns:
            List[Any]: The output from the dbally engine or an empty list if dbally was not in tool_calls. The Any type
            should be replaced with a dataclass specific to the LLM model containing the output of the function.

        Raises:
            FunctionCallingError: If an error occurs during function execution and `raise_exception` flag is set to True
        """

    @abstractmethod
    def process_functions_execution(self, functions_executions: List[Any]) -> List[Dict[str, str]]:
        """The result of process_response function may contain values that are not JSON serializable
        or not compliant with the LLM provider API. This function should process the functions_executions
        and return the values that are compliant with LLM provider API and can be sent back to the LLM.

        Args:
            functions_executions (List[Any]): Results of `process_response` function

        Returns:
            List[Dict[str, Any]]: Parsed functions_execution compliant with LLM provider API
        """

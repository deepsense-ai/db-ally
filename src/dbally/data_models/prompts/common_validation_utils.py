import re
from typing import Dict, List, Set, Tuple

ChatFormat = Tuple[Dict[str, str], ...]


class PromptTemplateError(Exception):
    """Error raised on incorrect PromptTemplate construction"""


def _extract_variables(text: str) -> List[str]:
    """
    Given a text string, extract all variables that can be filled using .format

    Args:
        text: string to process

    Returns:
        list of variables extracted from text
    """
    pattern = r"\{([^}]+)\}"
    return re.findall(pattern, text)


def _check_prompt_variables(chat: ChatFormat, variables_to_check: Set[str]) -> ChatFormat:
    """
    Function validates a given chat to make sure it contains variables required.

    Args:
        chat: chat to validate
        variables_to_check: set of variables to assert

    Raises:
        PromptTemplateError: If required variables are missing

    Returns:
        Chat, if it's valid.
    """
    variables = []
    for message in chat:
        content = message["content"]
        variables.extend(_extract_variables(content))
    if not set(variables_to_check).issubset(variables):
        raise PromptTemplateError(
            "Cannot build a prompt template from the provided chat, "
            "because it lacks necessary string variables. "
            "You need to format the following variables: {variables_to_check}"
        )
    return chat

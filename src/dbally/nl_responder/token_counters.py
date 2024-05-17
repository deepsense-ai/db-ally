from typing import Dict

from litellm import token_counter

from dbally.prompts import ChatFormat


def count_tokens(messages: ChatFormat, fmt: Dict[str, str], model: str) -> int:
    """
    Counts the number of tokens in the messages for OpenAIs' models.

    Args:
        messages: Messages to count tokens for.
        fmt: Arguments to be used with prompt.
        model: Model name.

    Returns:
        Number of tokens in the messages.
    """
    return sum(token_counter(model=model, text=message["content"].format(**fmt)) for message in messages)

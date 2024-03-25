from typing import Dict

from dbally.data_models.prompts.common_validation_utils import ChatFormat


def count_tokens_for_openai(messages: ChatFormat, fmt: Dict[str, str], model: str) -> int:
    """
    Counts the number of tokens in the messages for OpenAIs' models.

    Args:
        messages: Messages to count tokens for.
        fmt: Arguments to be used with prompt.
        model: Model name.

    Returns:
        Number of tokens in the messages.

    Raises:
        ImportError: If tiktoken package is not installed.
    """

    try:
        import tiktoken  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError("You need to install tiktoken package to use GPT models") from exc

    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows "<im_start>{role/name}\n{content}<im_end>\n"
        num_tokens += len(encoding.encode(message["content"].format(**fmt)))

    num_tokens += 2  # every reply starts with "<im_start>assistant"
    return num_tokens


def count_tokens_for_huggingface(messages: ChatFormat, fmt: Dict[str, str], model: str) -> int:
    """
    Counts the number of tokens in the messages for models available on HuggingFace.

    Args:
        messages: Messages to count tokens for.
        fmt: Arguments to be used with prompt.
        model: Model name.

    Returns:
        Number of tokens in the messages.

    Raises:
        ImportError: If transformers package is not installed.
    """

    try:
        from transformers import AutoTokenizer  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError("You need to install transformers package to use huggingface models' tokenizers.") from exc

    tokenizer = AutoTokenizer.from_pretrained(model)

    for message in messages:
        message["content"] = message["content"].format(**fmt)

    return len(tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True))

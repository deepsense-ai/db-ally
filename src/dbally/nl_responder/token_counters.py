from typing import Dict

from dbally.data_models.prompts.common_validation_utils import ChatFormat, PromptTemplateError


def count_tokens_for_openai(messages: ChatFormat, fmt: Dict[str, str], model: str) -> int:
    """
    Counts the number of tokens in the messages.
    
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
        import tiktoken
    except ImportError as exc:
        raise ImportError("You need to install tiktoken package to use GPT models") from exc
    
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for content in message.values():
            num_tokens += len(encoding.encode(content.format(**fmt)))
            
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

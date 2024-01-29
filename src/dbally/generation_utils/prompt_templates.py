from typing import Dict, List

from dbally.constants import GenerationModelType, PromptType

GPT4_PROMPTS: Dict[PromptType, List[Dict[str, str]]] = {
    PromptType.TEXT2SQL: [
        {
            "role": "system",
            "content": (
                "You are given the following SQL tables:" "\n\n{schema}\n\n"
                "Your job is to write queries given a user’s request."
                "Please return only the query, do not provide any extra text or explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                "{question}"
            ),
        },
    ]
}

PROMPT_TEMPLATES: Dict[GenerationModelType, Dict[PromptType, List[Dict[str, str]]]] = {
    GenerationModelType.GPT4: GPT4_PROMPTS
}

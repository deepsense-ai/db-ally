from typing import Dict, List

from dbally.constants import GenerationModelType, PromptType

GPT4_PROMPTS: Dict[PromptType, List[Dict[str, str]]] = {
    PromptType.TEXT2SQL: [
        {
            "role": "system",
            "content": (
                "Given the following SQL tables, your job is to write queries given a user’s request.:" "\n\n{schema}"
            ),
        },
        {
            "role": "user",
            "content": (
                "Write a SQL query which fetches data for the following question: {question}. \n"
                "Please return only the query, do not provide any extra text or explanation."
            ),
        },
    ]
}

PROMPT_TEMPLATES: Dict[GenerationModelType, Dict[PromptType, List[Dict[str, str]]]] = {
    GenerationModelType.GPT4: GPT4_PROMPTS
}

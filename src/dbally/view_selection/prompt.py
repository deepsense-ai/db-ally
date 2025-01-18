from ragbits.core.prompt import Prompt
from pydantic import BaseModel


class ViewSelectionPromptInput(BaseModel):
    question: str
    views: dict[str, str]


class ViewSelectionPrompt(Prompt[ViewSelectionPromptInput, str]):
    system_prompt = """
        You are a very smart database programmer.
        You have access to an API that lets you query a database:
        First you need to select a class to query, based on its description and the user question.
        You have the following classes to choose from:
        {% for name, description in views.items() %}
            {{ name }}: {{ description }}
        {% endfor %}
        Return only the selected view name. Don't give any comments.
        You can only use the classes that were listed.
        If none of the classes listed can be used to answer the user question, say `NoViewFoundError`
    """

    user_prompt = "{{ question }}"

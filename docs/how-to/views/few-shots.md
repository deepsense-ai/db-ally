# How-To: Define few shots

There are many ways to improve the accuracy of IQL generation - one of them is to use few-shot prompting. db-ally allows you to inject few-shot examples for any type of defined view, both structured and freeform.

Few shots are defined in the [`list_few_shots`](../../reference/views/index.md#dbally.views.base.BaseView.list_few_shots) method, each few shot example should be an instance of [`FewShotExample`](../../reference/prompt.md#dbally.prompt.elements.FewShotExample) class that defines example question and expected LLM answer.

## Structured views

For structured views, both questions and answers for [`FewShotExample`](../../reference/prompt.md#dbally.prompt.elements.FewShotExample) can be defined as a strings, whereas in case of answers Python expressions are also allowed (please see lambda function in example below).

```python
from dbally.prompt.elements import FewShotExample
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

class RecruitmentView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def list_few_shots(self) -> List[FewShotExample]:
        return [
            FewShotExample(
                "Which candidates studied at University of Toronto?",
                'studied_at("University of Toronto")',
            ),
            FewShotExample(
                "Do we have any soon available perfect fits for senior data scientist positions?",
                lambda: (
                    self.is_available_within_months(1)
                    and self.data_scientist_position()
                    and self.has_seniority("senior")
                ),
            ),
            ...
        ]
```

## Freeform views

Currently freeform views accept SQL query syntax as a raw string. The larger variety of passing parameters is considered to be implemented in further db-ally releases.

```python
from dbally.prompt.elements import FewShotExample
from dbally.views.freeform.text2sql import BaseText2SQLView

class RecruitmentView(BaseText2SQLView):
    """
    A view for retrieving candidates from the database.
    """

    def list_few_shots(self) -> List[FewShotExample]:
        return [
            FewShotExample(
                "Which candidates studied at University of Toronto?",
                'SELECT name FROM candidates WHERE university = "University of Toronto"',
            ),
            FewShotExample(
                "Which clients are from NY?",
                'SELECT name FROM clients WHERE city = "NY"',
            ),
            ...
        ]
```

## Prompt format

By default each few shot is injected subsequent to a system prompt message. The format is as follows:

```python
[
    {
        "role" "user",
        "content": "Question",
    },
    {
        "role": "assistant",
        "content": "Answer",
    }
]
```

If you use `examples` formatting tag in content field of the system or user message, all examples are going to be injected inside the message without additional conversation.

The example of prompt utilizing `examples` tag:

```python
[
    {
        "role" "system",
        "content": "Here are example resonses:\n {examples}",
    },
]
```

!!!info
    There is no best way to inject a few shot example. Different models can behave diffrently based on few shots formatting of choice.
    Generally, first appoach should yield the best results in most cases. Therefore, adding example tags in your custom prompts is not recommended.

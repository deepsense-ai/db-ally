from typing import Any, Dict, List

import pandas as pd

from dbally.prompts.elements import FewShotExample
from dbally.prompts.prompt_template import PromptTemplate
from dbally.views.exposed_functions import ExposedFunction


def _promptify_filters(filters: List[ExposedFunction]) -> str:
    """
    Formats filters for prompt.

    Args:
        filters: List of filters exposed by the view.

    Returns:
        Filters formatted for prompt.
    """
    return "\n".join([str(filter) for filter in filters])


def _promptify_views(views: Dict[str, str]) -> str:
    """
    Formats views for prompt.

    Args:
        views: Dictionary of available view names with corresponding descriptions.

    Returns:
        Views formatted for prompt.
    """
    return "\n".join([f"{name}: {description}" for name, description in views.items()])


def _promptify_results(results: List[Dict]) -> str:
    """
    Formats results into a markdown table.

    Args:
        results: List of results to be formatted.

    Returns:
        Results formatted as a markdown table.
    """
    df = pd.DataFrame.from_records(results)
    return df.to_markdown(index=False, headers="keys", tablefmt="psql")


class InputFormatter:
    """
    Generic formatter for prompt allowing to inject few shot examples into the conversation.
    """

    def __init__(self, examples: List[FewShotExample] = None) -> None:
        """
        Constructs a new InputFormatter instance.

        Args:
            examples: List of examples to be injected into the conversation.
        """
        self._examples = examples or []

    def __call__(self, template: PromptTemplate) -> PromptTemplate:
        """
        Applies formatting to the prompt template and adds few shot examples.

        Args:
            template: Prompt template with conversation and response parsing configuration.

        Returns:
            Formatted prompt template.
        """
        for example in self._examples:
            template = template.add_few_shot_message(example)
        return template.format_prompt({key: value for key, value in self.__dict__.items() if not key.startswith("_")})


class IQLInputFormatter(InputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        filters: List[ExposedFunction],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new IQLInputFormatter instance.

        Args:
            question: Question to be asked.
            filters: List of filters exposed by the view.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.filters = _promptify_filters(filters)


class ViewSelectionInputFormatter(InputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        views: Dict[str, str],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new ViewSelectionInputFormatter instance.

        Args:
            question: Question to be asked.
            views: Dictionary of available view names with corresponding descriptions.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.views = _promptify_views(views)


class NLResponderInputFormatter(InputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        results: List[Dict[str, Any]],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new NLResponderInputFormatter instance.

        Args:
            question: Question to be asked.
            results: List of results returned by the query.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.results = _promptify_results(results)


class QueryExplainerInputFormatter(InputFormatter):
    """
    Formats provided parameters to a form acceptable by default IQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        context: Dict[str, Any],
        results: List[Dict[str, Any]],
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new QueryExplainerInputFormatter instance.

        Args:
            question: Question to be asked.
            context: Context of the query.
            results: List of results returned by the query.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.query = next((context.get(key) for key in ("iql", "sql", "query") if context.get(key)), question)
        self.number_of_results = len(results)

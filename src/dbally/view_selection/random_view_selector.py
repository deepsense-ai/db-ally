import random
from typing import Dict, Optional

from dbally.view_selection.base import ViewSelector

from ragbits.core.options import Options

class RandomViewSelector(ViewSelector):
    """
    Mock View Selector selecting a random view.
    """

    # pylint: disable=unused-argument
    async def select_view(
        self,
        question: str,
        views: Dict[str, str],
        llm_options: Optional[Options] = None,
    ) -> str:
        """
        Dummy implementation returning random view.

        Args:
            question: user question.
            views: dictionary of available view names with corresponding descriptions.
            llm_options: options to use for the LLM client.

        Returns:
            random view name.
        """
        selected = random.choice(list(views.keys()))  # nosec
        print(f"For question: {question} I've randomly selected view: {selected}")
        return selected

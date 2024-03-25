# LLMViewSelector

The `LLMViewSelector` class is a component designed to leverage the power of LLMs to select the most suitable view for addressing user queries. Its primary function is to determine the optimal view that can effectively be used to answer a user's question.

The method used to select the most relevant view is [`self.select_view`](#dbally.view_selection.llm_view_selector.LLMViewSelector.select_view). It formats views using [`_promptify_views`](#dbally.view_selection.llm_view_selector._promptify_views) and then calls LLM Client, ultimately returning the name of the most suitable view.

::: dbally.view_selection.llm_view_selector.LLMViewSelector

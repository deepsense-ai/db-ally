# IQL Generator

In db-ally, LLM uses IQL (Intermediate Query Language) to express complex queries in a simplified way. The class used to generate IQL from nautral language query is `IQLGenerator`.

IQL generation is done using the method `self.genrate_iql`(#dbally.iql_generator.iql_generator.IQLGenerator.generate_iql). It uses LLM to generate text-based responses, passing in the prompt template, formatted filters, and user question.

!!! tip
    More details about IQL can be found [here](../concepts/iql.md).

::: dbally.iql_generator.iql_generator.IQLGenerator

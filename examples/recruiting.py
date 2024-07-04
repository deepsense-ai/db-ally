import asyncio
from dataclasses import dataclass
from typing import List

from recruiting.db import ENGINE, fill_candidate_table, get_recruitment_db_description
from recruiting.views import RecruitmentView

import dbally
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.audit.event_tracker import EventTracker
from dbally.llms.litellm import LiteLLM
from dbally.prompt import PromptTemplate
from dbally.prompt.elements import FewShotExample
from dbally.prompt.template import PromptFormat


class Text2SQLPromptFormat(PromptFormat):
    """
    Formats provided parameters to a form acceptable by SQL prompt.
    """

    def __init__(
        self,
        *,
        question: str,
        schema: str,
        examples: List[FewShotExample] = None,
    ) -> None:
        """
        Constructs a new Text2SQLInputFormat instance.

        Args:
            question: Question to be asked.
            schema: SQL schema description.
            examples: List of examples to be injected into the conversation.
        """
        super().__init__(examples)
        self.question = question
        self.schema = schema


TEXT2SQL_PROMPT_TEMPLATE = PromptTemplate[Text2SQLPromptFormat](
    (
        {
            "role": "system",
            "content": (
                "You are given the following SQL tables:"
                "\n\n{schema}\n\n"
                "Your job is to write queries given a user’s request."
                "Please return only the query, do not provide any extra text or explanation."
            ),
        },
        {
            "role": "user",
            "content": ("{question}"),
        },
    )
)


@dataclass
class Question:
    """
    A question to be asked to the recruitment database.
    """

    dbally_question: str
    gpt_question: str = ""


class Benchmark:
    """
    A benchmark for comparison of dbally and end2end gpt based text2sql.
    """

    def __init__(self) -> None:
        self._questions: List[Question] = []

    @property
    def questions(self) -> List[Question]:
        """List of benchmark questions

        Raises:
            ValueError: If no questions are added to the benchmark

        Returns:
            List[Question]: List of benchmark questions
        """
        if self._questions:
            return self._questions

        raise ValueError("No questions added to the benchmark")

    def add_question(self, question: Question) -> None:
        """Adds a question to the benchmark.

        Args:
            question (Question): A question to be added to the benchmark
        """
        self._questions.append(question)


example_benchmark = Benchmark()
example_benchmark.add_question(Question(dbally_question="Give candidates with more than 5 years of experience"))
example_benchmark.add_question(
    Question(
        dbally_question="Return candidates available for senior positions",
        gpt_question="Return me candidates available for senior positions.\
            Seniors have more than 5 years of experience",
    )
)
example_benchmark.add_question(Question(dbally_question="List candidates from Europe"))
example_benchmark.add_question(Question(dbally_question="Who studied at Stanford?"))
example_benchmark.add_question(
    Question(
        dbally_question="Do we have any perfect fits\
                                        for data scientist positions?"
    )
)


async def recruiting_example(db_description: str, benchmark: Benchmark = example_benchmark) -> None:
    """Runs a recruiting example which compares dbally and end2end gpt based text2sql.

    Args:
        db_description (str): database schema description,used to generate prompts for gpt.
        benchmark (Benchmark, optional): Benchmark containing set of questions. Defaults to example_benchmark.
    """

    recruitment_db = dbally.create_collection(
        "recruitment",
        llm=LiteLLM(),
        event_handlers=[CLIEventHandler()],
    )
    recruitment_db.add(RecruitmentView, lambda: RecruitmentView(ENGINE))

    event_tracker = EventTracker()
    llm = LiteLLM("gpt-4")

    for question in benchmark.questions:
        await recruitment_db.ask(question.dbally_question, return_natural_response=True)
        gpt_question = question.gpt_question if question.gpt_question else question.dbally_question

        prompt_format = Text2SQLPromptFormat(question=gpt_question, schema=db_description)
        formatted_prompt = TEXT2SQL_PROMPT_TEMPLATE.format_prompt(prompt_format)
        gpt_response = await llm.generate_text(formatted_prompt, event_tracker=event_tracker)

        print(f"GPT response: {gpt_response}")


def run_recruiting_example(db_description: str = "", benchmark: Benchmark = example_benchmark) -> None:
    """Runs the recruiting example.

    Args:
        db_description (str, optional): database schema description, used to generate prompts for gpt. Defaults to "".
        benchmark (Benchmark, optional): Benchmark containing set of questions. Defaults to example_benchmark.
    """
    fill_candidate_table()
    asyncio.run(recruiting_example(db_description, benchmark))


if __name__ == "__main__":
    db_desc = get_recruitment_db_description()

    run_recruiting_example(db_desc)

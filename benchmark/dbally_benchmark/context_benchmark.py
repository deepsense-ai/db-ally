# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring
import polars as pl

import dbally
import asyncio
import typing
import json
import traceback
import os
import tqdm.asyncio
import sqlalchemy
from typing_extensions import TypeAlias
from copy import deepcopy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base, AutomapBase
from dataclasses import dataclass, field

from dbally import decorators, SqlAlchemyBaseView
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.llms.litellm import LiteLLM
from dbally.context import BaseCallerContext
from dbally.iql import IQLError


SQLITE_DB_FILE_REL_PATH = "../../examples/recruiting/data/candidates.db"
engine = create_engine(f"sqlite:///{os.path.abspath(SQLITE_DB_FILE_REL_PATH)}")

Base: AutomapBase = automap_base()
Base.prepare(autoload_with=engine)

Candidate = Base.classes.candidates


@dataclass
class MyData(BaseCallerContext):
    first_name: str
    surname: str
    position: str
    years_of_experience: int
    university: str
    skills: typing.List[str]
    country: str


@dataclass
class OpenPosition(BaseCallerContext):
    position: str
    min_years_of_experience: int
    graduated_from_university: str
    required_skills: typing.List[str]


class CandidateView(SqlAlchemyBaseView):
    """
    A view for retrieving candidates from the database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return sqlalchemy.select(Candidate)

    @decorators.view_filter()
    def at_least_experience(self, years: typing.Union[int, OpenPosition]) -> sqlalchemy.ColumnElement:
        """
        Filters candidates with at least `years` of experience.
        """
        if isinstance(years, OpenPosition):
            years = years.min_years_of_experience

        return Candidate.years_of_experience >= years

    @decorators.view_filter()
    def at_most_experience(self, years: typing.Union[int, MyData]) -> sqlalchemy.ColumnElement:
        if isinstance(years, MyData):
            years = years.years_of_experience

        return Candidate.years_of_experience <= years

    @decorators.view_filter()
    def has_position(self, position: typing.Union[str, OpenPosition]) -> sqlalchemy.ColumnElement:
        if isinstance(position, OpenPosition):
            position = position.position

        return Candidate.position == position

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> sqlalchemy.ColumnElement:
        """
        Filters candidates that can be considered for a senior data scientist position.
        """
        return sqlalchemy.and_(
            Candidate.position.in_(["Data Scientist", "Machine Learning Engineer", "Data Engineer"]),
            Candidate.years_of_experience >= 3,
        )

    @decorators.view_filter()
    def from_country(self, country: typing.Union[str, MyData]) -> sqlalchemy.ColumnElement:
        """
        Filters candidates from a specific country.
        """
        if isinstance(country, MyData):
            return Candidate.country == country.country

        return Candidate.country == country

    @decorators.view_filter()
    def graduated_from_university(self, university: typing.Union[str, MyData]) -> sqlalchemy.ColumnElement:
        if isinstance(university, MyData):
            university = university.university

        return Candidate.university == university

    @decorators.view_filter()
    def has_skill(self, skill: str) -> sqlalchemy.ColumnElement:
        return Candidate.skills.like(f"%{skill}%")

    @decorators.view_filter()
    def knows_data_analysis(self) -> sqlalchemy.ColumnElement:
        return Candidate.tags.like("%Data Analysis%")

    @decorators.view_filter()
    def knows_python(self) -> sqlalchemy.ColumnElement:
        return Candidate.skills.like("%Python%")

    @decorators.view_filter()
    def first_name_is(self, first_name: typing.Union[str, MyData]) -> sqlalchemy.ColumnElement:
        if isinstance(first_name, MyData):
            first_name = first_name.first_name

        return Candidate.name.startswith(first_name)


OpenAILLMName: TypeAlias = typing.Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-instruct', 'gpt-4-turbo', 'gpt-4o']


def setup_collection(model_name: OpenAILLMName) -> dbally.Collection:
    llm = LiteLLM(model_name=model_name)

    collection = dbally.create_collection("recruitment", llm)
    collection.add(CandidateView, lambda: CandidateView(engine))

    return collection


async def generate_iql_from_question(
    collection: dbally.Collection,
    model_name: OpenAILLMName,
    question: str,
    contexts: typing.Optional[typing.List[BaseCallerContext]]
) -> typing.Tuple[str, OpenAILLMName, typing.Optional[str]]:

    try:
        result = await collection.ask(
            question,
            contexts=contexts,
            dry_run=True
        )
    except IQLError as e:
        exc_pretty = traceback.format_exception_only(e.__class__, e)[0]
        return question, model_name, f"FAILED: {exc_pretty}({e.source})"
    except Exception as e:
        exc_pretty = traceback.format_exception_only(e.__class__, e)[0]
        return question, model_name, f"FAILED: {exc_pretty}"

    out = result.metadata.get("iql")
    if out is None:
        return question, model_name, None

    return question, model_name, out.replace('"', '\'')


@dataclass
class BenchmarkConfig:
    dataset_path: str
    out_path: str
    n_repeats: int = 5
    llms: typing.List[OpenAILLMName] = field(default_factory=lambda: ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o'])


async def main(config: BenchmarkConfig):
    test_set = None
    with open(config.dataset_path, 'r') as file:
        test_set = json.load(file)

    contexts = [
        MyData(
            first_name="John",
            surname="Smith",
            years_of_experience=4,
            position="Data Engineer",
            university="University of Toronto",
            skills=["Python"],
            country="United Kingdom"
        ),
        OpenPosition(
            position="Machine Learning Engineer",
            graduated_from_university="Stanford Univeristy",
            min_years_of_experience=1,
            required_skills=["Python", "SQL"]
        )
    ]

    tasks: typing.List[asyncio.Task] = []
    for model_name in config.llms:
        collection = setup_collection(model_name)
        for test_case in test_set:
            answers = []
            for _ in range(config.n_repeats):
                task = asyncio.create_task(generate_iql_from_question(collection, model_name,
                                                                      test_case["question"], contexts=contexts))
                tasks.append(task)

    output_data = {
        test_case["question"]:test_case
        for test_case in test_set
    }
    empty_answers = {str(llm_name): [] for llm_name in config.llms}

    total_iter = len(config.llms) * len(test_set) * config.n_repeats
    for task in tqdm.asyncio.tqdm.as_completed(tasks, total=total_iter):
        question, llm_name, answer = await task
        if "answers" not in output_data[question]:
            output_data[question]["answers"] = deepcopy(empty_answers)

        output_data[question]["answers"][llm_name].append(answer)

    df_out_raw =  pl.DataFrame(list(output_data.values()))

    df_out = (
        df_out_raw
        .unnest("answers")
        .unpivot(
            on=pl.selectors.starts_with("gpt"),
            index=["question", "correct_answer", "context"],
            variable_name="model",
            value_name="answer"
        )
        .explode("answer")
        .group_by(["context", "model"])
        .agg([
            (pl.col("correct_answer") == pl.col("answer")).mean().alias("frac_hits"),
            (pl.col("correct_answer") == pl.col("answer")).sum().alias("n_hits"),
        ])
        .sort(["model", "context"])
    )

    print(df_out)

    with open(config.out_path, 'w') as file:
        file.write(json.dumps(df_out_raw.to_dicts(), indent=2))


if __name__ == "__main__":
    config = BenchmarkConfig(
        dataset_path="dataset/context_dataset.json",
        out_path="../../context_benchmark_output.json"
    )

    asyncio.run(main(config))

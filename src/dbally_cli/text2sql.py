import asyncio
import importlib
import os
from typing import Callable, Optional, Union

import click
import sqlalchemy
from click import BadParameter, Context, Option
from sqlalchemy import Column, Engine, Table
from sqlalchemy.exc import ArgumentError

from dbally.embeddings.litellm import LiteLLMEmbeddingClient
from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLM
from dbally.similarity.faiss_store import FaissStore
from dbally.similarity.index import SimilarityIndex
from dbally.similarity.sqlalchemy_base import SimpleSqlAlchemyFetcher
from dbally_codegen.autodiscovery import configure_text2sql_auto_discovery
from dbally_codegen.generator import Text2SQLViewGenerator


def faiss_builder(engine: sqlalchemy.Engine, table: sqlalchemy.Table, column: sqlalchemy.Column) -> SimilarityIndex:
    """
    Build a Faiss store.

    Args:
        engine: The SQLAlchemy engine.
        table: The table.
        column: The column.

    Returns:
        The Faiss store.
    """
    return SimilarityIndex(
        fetcher=SimpleSqlAlchemyFetcher(
            sqlalchemy_engine=engine,
            column=column,
            table=table,
        ),
        store=FaissStore(
            index_dir=".",
            index_name=f"{table.name}_{column.name}_index",
            embedding_client=LiteLLMEmbeddingClient(),
        ),
    )


def validate_file_path(_ctx: Context, _param: Option, value: str) -> str:
    """
    Validate the file path.

    Args:
        value: The value of the option.

    Returns:
        The validated file path.
    """
    root, ext = os.path.splitext(value)
    if not ext:
        ext = ".py"
    elif ext != ".py":
        raise BadParameter("file extension must be '.py'.")
    return f"{root}{ext}"


def validate_db_url(_ctx: Context, _param: Option, value: Union[str, Engine]) -> Engine:
    """
    Validate the database connection string.

    Args:
        value: The value of the option.

    Returns:
        The validated database connection string.
    """
    if isinstance(value, Engine):
        return value
    if not value:
        raise BadParameter("database connection string is required.")

    try:
        return sqlalchemy.create_engine(value)
    except ArgumentError as exc:
        raise BadParameter("invalid database connection string.") from exc


def validate_llm_object(_ctx: Context, _param: Option, value: Union[str, LLM]) -> Optional[LLM]:
    """ "
    Validate the LLM object.

    Args:
        value: The value of the option.

    Returns:
        The validated LLM object.
    """
    if isinstance(value, LLM):
        return value
    if value == "None" or value is None:
        return None
    if value.startswith("litellm:"):
        return LiteLLM(value.split(":")[1])

    llm = load_object(value)
    if not isinstance(llm, LLM):
        raise BadParameter("The LLM object must be an instance of the LLM class.")
    return llm


def validate_similarity_index_factory(
    _ctx: Context, _param: Option, value: Union[str, Callable[[Engine, Table, Column], SimilarityIndex]]
) -> Optional[Callable[[Engine, Table, Column], SimilarityIndex]]:
    """
    Validate the similarity index factory.

    Args:
        value: The value of the option.

    Returns:
        The validated similarity index factory.
    """
    if callable(value):
        return value
    if value == "None" or value is None:
        return None
    if value == "faiss":
        return faiss_builder

    index_builder = load_object(value) if value else None
    if not callable(index_builder):
        raise BadParameter("The similarity index factory must be a callable object.")
    return index_builder


@click.command(help="Generate a Text2SQL view definition file.")
@click.option(
    "--file_path",
    default="text2sql_view.py",
    show_default=True,
    prompt="File path",
    help="The path to the file where the view will be generated.",
    callback=validate_file_path,
)
@click.option(
    "--db",
    default="sqlite://",
    show_default=True,
    prompt="Database URL",
    help="The database connection string.",
    callback=validate_db_url,
    type=click.UNPROCESSED,
)
@click.option(
    "--llm",
    default="None",
    show_default=True,
    prompt="LLM object",
    help="The path to the LLM object.",
    callback=validate_llm_object,
    type=click.UNPROCESSED,
)
@click.option(
    "--llm_description",
    is_flag=True,
    default=False,
    show_default=True,
    prompt="LLM table description?",
    help="Generate tables description using LLM.",
)
@click.option(
    "--similarity_index_factory",
    default="None",
    show_default=True,
    prompt="Similarity index factory",
    help="The path to the similarity index factory.",
    callback=validate_similarity_index_factory,
    type=click.UNPROCESSED,
)
def generate_text2sql_view(
    file_path: str,
    db: Engine,
    llm: Optional[LLM],
    llm_description: bool,
    similarity_index_factory: Optional[Callable[[Engine, sqlalchemy.Table, sqlalchemy.Column], SimilarityIndex]],
) -> None:
    """
    Generate a Text2SQL view definition file.

    Args:
        file_path: The path to the file where the view will be generated.
        db: The database connection string.
        llm: The path to the LLM object.
        llm_description: Generate a description using the LLM object.
        similarity_index_factory: The path to the similarity index factory.
    """
    builder = configure_text2sql_auto_discovery(db)
    if llm:
        builder = builder.use_llm(llm)
        if llm_description:
            builder = builder.generate_description_by_llm()
        if similarity_index_factory:
            builder = builder.suggest_similarity_indexes(similarity_index_factory)

    click.echo("Discovering tables...")
    tables = asyncio.run(builder.discover())
    click.echo(f"Discovered {len(tables)} tables.")

    click.echo("Generating Text2SQL view...")
    generator = Text2SQLViewGenerator(tables)
    code = generator.generate()

    dirs, _ = os.path.split(file_path)
    if dirs:
        os.makedirs(dirs, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(code)

    click.echo(f"Generated Text2SQL view in {file_path}.")


def load_object(path: str) -> object:
    """
    Load an object from a module.

    Args:
        path: The path to the object in the format 'module:object'.

    Returns:
        The object.

    Raises:
        BadParameter: If the object is not found.
    """
    try:
        module_name, object_name = path.split(":")
    except ValueError as exc:
        raise BadParameter("The object must be in the format 'module:object'.") from exc

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise BadParameter(f"Could not find the module '{module_name}'.") from exc

    try:
        return getattr(module, object_name)
    except AttributeError as exc:
        raise BadParameter(f"Could not find the '{object_name}' object in the '{module_name}' module.") from exc

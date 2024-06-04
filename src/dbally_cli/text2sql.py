import asyncio
import importlib
import os
import sys

import click
import sqlalchemy

from dbally.llms.base import LLM
from dbally_codegen.autodiscovery import configure_text2sql_auto_discovery
from dbally_codegen.generator import Text2SQLViewGenerator
from examples.recruting.db import fill_candidate_table


@click.command(help="Generate a Text2SQL view definition file.")
@click.option(
    "--file_path",
    default="text2sql_view.py",
    prompt="File path",
    help="The path to the file where the view will be generated.",
)
@click.option(
    "--db_url",
    default="sqlite://",
    prompt="Database connection string",
    help="The database connection string.",
)
@click.option(
    "--llm_object",
    default="examples.rec:llm",
    prompt="LLM object",
    help="The path to the LLM object.",
)
@click.option(
    "--llm_description",
    is_flag=True,
    prompt="Generate description using LLM object?",
    help="Generate a description using the LLM object.",
)
@click.option(
    "--similarity_index_factory",
    default="examples.rec:index_builder",
    prompt="Similarity index factory",
    help="The path to the similarity index factory.",
)
def generate_text2sql_view(
    file_path: str,
    db_url: str,
    llm_object: str,
    llm_description: bool,
    similarity_index_factory: str,
) -> None:
    """
    Generate a Text2SQL view definition file.

    Args:
        file_path: The path to the file where the view will be generated.
        db_url: The database connection string.
        llm_object: The path to the LLM object.
        llm_description: Generate a description using the LLM object.
        similarity_index_factory: The path to the similarity index factory.
    """
    click.echo("Generating Text2SQL view...")

    root, ext = os.path.splitext(file_path)
    if not ext:
        ext = ".py"
    elif ext != ".py":
        click.echo("The file extension must be '.py'.")
        sys.exit(1)
    file_path = f"{root}{ext}"

    engine = sqlalchemy.create_engine(db_url)
    fill_candidate_table(engine)

    llm = load_object(llm_object) if llm_object else None
    index_builder = load_object(similarity_index_factory) if similarity_index_factory else None

    if not isinstance(llm, LLM):
        click.echo("The LLM object must be an instance of the LLM class.")
        sys.exit(1)

    if not callable(index_builder):
        click.echo("The similarity index factory must be a callable object.")
        sys.exit(1)

    builder = configure_text2sql_auto_discovery(engine)
    if llm:
        builder = builder.use_llm(llm)
        if llm_description:
            builder = builder.generate_description_by_llm()
        if index_builder:
            builder = builder.suggest_similarity_indexes(index_builder)

    tables = asyncio.run(builder.discover())
    generator = Text2SQLViewGenerator(tables)
    code = generator.generate()

    dirs, _ = os.path.split(file_path)
    if dirs:
        os.makedirs(dirs, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(code)

    click.echo(f"Finished generating Text2SQL view in {file_path}.")


def load_object(path: str) -> object:
    """
    Load an object from a module.

    Args:
        path: The path to the object in the format 'module:object'.

    Returns:
        The object.
    """
    try:
        module_name, object_name = path.split(":")
    except ValueError:
        click.echo("The object must be in the format 'module:object'.")
        sys.exit(1)

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        click.echo(f"Could not find the module '{module_name}'.")
        sys.exit(1)

    try:
        return getattr(module, object_name)
    except AttributeError:
        click.echo("Could not find the '{object_name}' object in the '{module_name}' module.")
        sys.exit(1)

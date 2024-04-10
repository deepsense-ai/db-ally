# pylint: disable=missing-param-doc
import asyncio
import sys

import click

from dbally.similarity.detector import SimilarityIndexDetector, SimilarityIndexDetectorException


@click.command(short_help="Updates similarity indexes based on the given object path.")
@click.argument("path")
def update_index(path: str):
    """
    Updates similarity indexes based on the given object path, looking for
    arguments on view filter methods that are annotated with similarity indexes.

    Works with method-based views that inherit from MethodsBaseView (including
    all built-in dbally views).

    The path take one of the following formats:
    - path.to.module
    - path.to.module:ViewName
    - path.to.module:ViewName.method_name
    - path.to.module:ViewName.method_name.argument_name

    Less specific path will cause more indexes to be updated. For example,
    - Path to a specific argument will update only the index for that argument.
    - Path to a specific method will update indexes of all arguments of that filter method.
    - Path to a specific view will update indexes of all arguments of all methods of that view.
    - Path to a module will update indexes of all arguments of all methods of all views of that module.
    """
    click.echo(f"Looking for similarity indexes in {path}...")

    try:
        updater = SimilarityIndexDetector.from_path(path)
        indexes = updater.list_indexes()
    except SimilarityIndexDetectorException as exc:
        click.echo(exc.message, err=True)
        sys.exit(1)

    if not indexes:
        click.echo("No similarity indexes found.", err=True)
        sys.exit(1)

    for index, index_users in indexes.items():
        click.echo(f"Updating index used by {', '.join(index_users)}...")
        asyncio.run(index.update())

    click.echo("Indexes updated successfully.")

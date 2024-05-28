import os
import sys

import click

from dbally_codegen.generator import Text2SQLViewGenerator


@click.command(short_help="Generate a Text2SQL view definition file.")
@click.argument("file_path")
def generate_text2sql_view(file_path: str) -> None:
    """
    Generate a Text2SQL view in the given path.

    Args:
        file_path: The path to the file where the view will be generated.
    """
    click.echo("Generating Text2SQL view.")

    root, ext = os.path.splitext(file_path)
    if not ext:
        ext = ".py"
    elif ext != ".py":
        click.echo("The file extension must be '.py'.")
        sys.exit(1)
    file_path = f"{root}{ext}"

    generator = Text2SQLViewGenerator()
    code = generator.generate()

    dirs, _ = os.path.split(file_path)
    os.makedirs(dirs, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(code)

    click.echo(f"Finished generating Text2SQL view in {file_path}.")

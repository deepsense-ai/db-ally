import click

from dbally_cli.text2sql import generate_text2sql_view


@click.group()
def cli() -> None:
    """
    Command line tool for interacting with dbally.
    """


cli.add_command(generate_text2sql_view)

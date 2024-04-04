import click

from dbally_cli.similarity import update_index


@click.group()
def cli():
    """Command line tool for interacting with Db-ally"""


cli.add_command(update_index)

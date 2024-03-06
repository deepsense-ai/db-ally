import click

from dbally_cli.example1 import example1
from dbally_cli.example2 import example2


@click.group()
def cli():
    """Command line tool for interacting with Db-ally"""


cli.add_command(example1)
cli.add_command(example2)

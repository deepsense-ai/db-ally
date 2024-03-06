# pylint: disable=missing-param-doc

import click


@click.command()
@click.option("--option1", help="This option serves as an example of how to use options in a command.")
def example2(option1: str):
    """Example command 1"""
    click.echo(f"Example command 2 with some option: {option1}")

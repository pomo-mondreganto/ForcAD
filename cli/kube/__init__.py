import click

from .setup import setup


@click.group('kube')
def cli():
    pass


cli: click.Group
cli.add_command(setup)

import click

from .setup import setup
from .start import start


@click.group('kube')
def cli():
    pass


cli: click.Group
cli.add_command(setup)
cli.add_command(start)

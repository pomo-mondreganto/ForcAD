import click

from .build import build
from .setup import setup
from .start import start


@click.group('kube')
def cli():
    pass


cli: click.Group
cli.add_command(build)
cli.add_command(setup)
cli.add_command(start)

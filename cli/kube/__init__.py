import click

from .build import build
from .create import create
from .destroy import destroy
from .setup import setup
from .start import start


@click.group('kube', help='Kubernetes-related commands (run kube --help for more)')
def cli():
    pass


cli: click.Group
cli.add_command(build)
cli.add_command(create)
cli.add_command(destroy)
cli.add_command(setup)
cli.add_command(start)

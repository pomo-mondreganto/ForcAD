import click

from .build import build
from .clean import clean
from .create import create
from .destroy import destroy
from .print_tokens import print_tokens
from .reset import reset
from .setup import setup
from .start import start
from .validate import validate


@click.group('kube', help='Kubernetes-related commands (run kube --help for more)')
def cli():
    pass


cli: click.Group  # noqa
cli.add_command(build)
cli.add_command(clean)
cli.add_command(create)
cli.add_command(destroy)
cli.add_command(print_tokens)
cli.add_command(reset)
cli.add_command(setup)
cli.add_command(start)
cli.add_command(validate)

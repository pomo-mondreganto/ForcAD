import click

from .build import build
from .pause import pause
from .print_tokens import print_tokens
from .reset import reset
from .resume import resume
from .run_docker import run_docker_command
from .scale import scale
from .setup import setup
from .start import start
from .worker import worker


@click.group()
def cli():
    pass


cli: click.Group
cli.add_command(setup)
cli.add_command(print_tokens)
cli.add_command(reset)
cli.add_command(build)
cli.add_command(start)
cli.add_command(scale)
cli.add_command(worker)
cli.add_command(pause)
cli.add_command(resume)
cli.add_command(run_docker_command)

__all__ = ('cli',)

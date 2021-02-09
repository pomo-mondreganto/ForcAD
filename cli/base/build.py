import click

from cli.options import with_fast_option
from cli.utils import run_docker


@click.command(help="Build the images, don't run")
@with_fast_option
def build(**_kwargs):
    run_docker(['build'])

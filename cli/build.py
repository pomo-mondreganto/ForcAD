import click

from .utils import run_docker, with_fast_option


@click.command(help="Build the images, don't run")
@with_fast_option
def build(**_kwargs):
    run_docker(['build'])

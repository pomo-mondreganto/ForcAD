import click

from .constants import VERSION
from .utils import run_docker, with_fast_option


@click.command(help='Start ForcAD, building if necessary')
@with_fast_option
@click.option(
    '-w', '--workers',
    type=int,
    metavar='N',
    default=1,
    help='Number of celery worker instances',
)
def start(workers, **_kwargs):
    click.echo(f'Using Forcad:{VERSION}')
    run_docker(['up', '--build', '-d', '--scale', f'celery={workers}'])

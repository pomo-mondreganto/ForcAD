import click

from .constants import VERSION
from .options import with_fast_option, with_workers_option
from .utils import run_docker


@click.command(help='Start ForcAD, building if necessary')
@with_fast_option
@with_workers_option
def start(workers, **_kwargs):
    click.echo(f'Using Forcad:{VERSION}')
    run_docker(['up', '--build', '-d', '--scale', f'celery={workers}'])

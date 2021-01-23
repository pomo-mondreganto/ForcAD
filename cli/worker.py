import click

from .scale import scale
from .setup import setup


@click.command(help='Start the workers only')
@click.option(
    '-f', '--fast',
    is_flag=True,
    help='Use faster build with prebuilt images',
)
@click.option(
    '-w', '--workers',
    type=int,
    metavar='N',
    default=1,
    help='Number of celery worker instances',
)
@click.option(
    '--redis',
    metavar='ADDR',
    help='Redis address for the worker',
    required=True,
)
@click.option(
    '--database',
    metavar='ADDR',
    help='Postgres address for the worker',
    required=True,
)
@click.option(
    '--rabbitmq',
    metavar='ADDR',
    help='RabbitMQ address for the worker',
    required=True,
)
@click.pass_context
def worker(ctx: click.Context, workers, **_kwargs):
    ctx.forward(setup)
    ctx.invoke(scale, service=(('celery', workers),))

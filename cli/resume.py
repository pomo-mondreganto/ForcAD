import click

from .utils import run_docker


@click.command(
    help='Start updating rounds & receiving flags (counterpart of pause_game command)',
)
def resume():
    run_docker(['start', 'celerybeat', 'tcp_receiver', 'http_receiver'])

import click

from cli.utils import run_docker


@click.command(
    help='Start updating rounds & receiving flags (counterpart of pause_game command)',
)
def resume():
    run_docker(['start', 'celerybeat', 'tcp-receiver', 'http-receiver'])
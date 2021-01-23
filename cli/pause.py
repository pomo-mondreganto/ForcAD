import click

from .utils import run_docker


@click.command(help='Stop updating rounds & receiving flags')
def pause():
    run_docker(['stop', 'celerybeat', 'tcp_receiver', 'http_receiver'])

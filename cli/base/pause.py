import click

from cli.utils import run_docker


@click.command(help='Stop updating rounds & receiving flags')
def pause():
    run_docker(['stop', 'ticker', 'http-receiver'])

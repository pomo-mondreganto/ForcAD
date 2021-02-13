import click

from cli.constants import FULL_COMPOSE_PATH, BASE_DIR
from cli.utils import get_output


@click.command('print_tokens', help='Print team tokens')
def print_tokens():
    command = [
        'docker-compose',
        '-f', FULL_COMPOSE_PATH,
        'exec', '-T', 'ticker',
        'python3', '/app/scripts/print_tokens.py',
    ]
    res = get_output(command, cwd=BASE_DIR).strip()
    click.echo(res)

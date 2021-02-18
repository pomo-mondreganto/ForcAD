import click

from cli.constants import FULL_COMPOSE_PATH, BASE_DIR
from cli.utils import run_command


@click.command('print_tokens', help='Print team tokens')
def print_tokens():
    command = [
        'docker-compose',
        '-f', FULL_COMPOSE_PATH,
        'exec', '-T', 'ticker',
        'python3', '/app/scripts/print_tokens.py',
    ]
    run_command(command, cwd=BASE_DIR)

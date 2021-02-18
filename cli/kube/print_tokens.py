import click

from cli.constants import BASE_DIR
from cli.utils import run_command


@click.command('print_tokens', help='Print team tokens')
def print_tokens():
    command = [
        'kubectl',
        '--namespace', 'forcad',
        'exec', 'deployment/ticker',
        '--', 'python3', '/app/scripts/print_tokens.py',
    ]
    run_command(command, cwd=BASE_DIR)

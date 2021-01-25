import subprocess

import click

from cli.constants import FULL_COMPOSE_PATH, BASE_DIR


@click.command('print_tokens', help='Print team tokens')
def print_tokens():
    command = [
        'docker-compose',
        '-f', FULL_COMPOSE_PATH,
        'exec', '-T', 'client-api',
        'python3', '/app/scripts/print_tokens.py',
    ]
    res = subprocess.check_output(
        command,
        cwd=BASE_DIR,
    )
    click.echo(res.decode().strip())

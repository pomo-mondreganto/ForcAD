import click

from cli.constants import BASE_DIR
from cli.utils import run_command


@click.command(help='Build images with Skaffold')
def build(**_kwargs):
    cmd = [
        'skaffold', 'build',
        '-f', 'deploy/skaffold.yml'
    ]
    run_command(cmd, cwd=BASE_DIR)

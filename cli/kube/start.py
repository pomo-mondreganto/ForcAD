import click

from cli.constants import BASE_DIR
from cli.utils import run_command


@click.command(help='Deploy to the the cluster using Skaffold')
@click.option(
    '--dev',
    is_flag=True,
    help='Use development configuration (with hot reload)',
)
def start(dev: bool, **_kwargs):
    cmd = [
        'skaffold',
        'dev' if dev else 'run',
        '-f', 'deploy/skaffold.yml'
    ]
    run_command(cmd, cwd=BASE_DIR)

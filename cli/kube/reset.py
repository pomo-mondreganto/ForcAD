import click

from cli.constants import BASE_DIR
from cli.utils import run_command


@click.command(help='Remove all kube-deployed resources')
def reset(**_kwargs):
    run_command(['skaffold', 'delete', '-f', 'deploy/skaffold.yml'], cwd=BASE_DIR)

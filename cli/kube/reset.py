import click

from cli import utils
from cli.constants import BASE_DIR
from cli.kube.clean import clean


@click.command(help='Remove all kube-deployed resources & clean up')
@click.pass_context
def reset(ctx: click.Context):
    utils.print_bold('Removing skaffold-created resources')
    utils.run_command(['skaffold', 'delete', '-f', 'deploy/skaffold.yml'], cwd=BASE_DIR)

    utils.print_bold('Cleaning up')
    ctx.invoke(clean)

    utils.print_success('Done!')

import subprocess

import click

from cli import constants, utils
from cli.base.clean import clean


@click.command(help='Reset the game & clean up')
@click.pass_context
def reset(ctx: click.Context):
    utils.print_bold('Trying to wipe the database')
    command = [
        'docker-compose',
        '-f', constants.FULL_COMPOSE_PATH,
        'run', 'initializer',
        'python3', '/app/scripts/reset_db.py',
    ]
    subprocess.run(
        command,
        cwd=constants.BASE_DIR,
        stdout=subprocess.DEVNULL,
        check=False,
    )

    utils.print_bold('Bringing down services')
    command = [
        'docker-compose',
        '-f', constants.FULL_COMPOSE_PATH,
        'down', '-v',
        '--remove-orphans',
    ]
    utils.run_command(command, cwd=constants.BASE_DIR)

    utils.print_bold('Running clean')
    ctx.invoke(clean)

    utils.print_success('Done!')

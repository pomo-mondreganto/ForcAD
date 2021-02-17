import shutil
import subprocess

import click

from cli import constants, utils


@click.command(help='Reset the game & clean up')
def reset():
    data_path = constants.BASE_DIR / 'docker_volumes' / 'postgres' / 'data'
    shutil.rmtree(data_path, onerror=utils.print_file_exception_info)

    command = [
        'docker-compose',
        '-f', constants.FULL_COMPOSE_PATH,
        'run', 'initializer',
        'python3', '/app/scripts/reset_db.py',
    ]
    print('Trying to wipe the database')
    subprocess.run(
        command,
        cwd=constants.BASE_DIR,
        stdout=subprocess.DEVNULL,
        check=False,
    )

    command = [
        'docker-compose',
        '-f', constants.FULL_COMPOSE_PATH,
        'down', '-v',
        '--remove-orphans',
    ]
    utils.run_command(command, cwd=constants.BASE_DIR)

    utils.print_success('Done')

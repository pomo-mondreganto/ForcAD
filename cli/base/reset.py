import shutil
import subprocess

import click

from cli.constants import BASE_DIR, FULL_COMPOSE_PATH
from cli.utils import print_file_exception_info, run_command


@click.command(help='Reset the game & clean up')
def reset():
    data_path = BASE_DIR / 'docker_volumes' / 'postgres' / 'data'
    shutil.rmtree(data_path, onerror=print_file_exception_info)

    command = [
        'docker-compose',
        '-f', FULL_COMPOSE_PATH,
        'run', 'initializer',
        'python3', '/app/scripts/reset_db.py',
    ]
    print('Trying to wipe the database')
    subprocess.run(
        command,
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        check=False,
    )

    command = [
        'docker-compose',
        '-f', FULL_COMPOSE_PATH,
        'down', '-v',
        '--remove-orphans',
    ]
    run_command(
        command,
        cwd=BASE_DIR,
    )

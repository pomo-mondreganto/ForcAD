import os
import subprocess
import sys
from functools import wraps
from typing import List, Tuple

import click
import yaml

from .constants import (
    BASE_DIR, CONFIG_PATH, VERSION,
    BASE_COMPOSE_FILE, FAST_COMPOSE_FILE, TESTS_COMPOSE_FILE,
)


def load_config():
    with CONFIG_PATH.open(mode='r') as f:
        config = yaml.safe_load(f)
    return config


def run_command(command: List[str], cwd=None, env=None):
    p = subprocess.Popen(command, cwd=cwd, env=env)
    rc = p.wait()
    if rc != 0:
        print('[-] Failed!')
        sys.exit(1)


def run_docker(args: List[str]):
    base = [
        'docker-compose',
        '-f', BASE_COMPOSE_FILE,
    ]

    ctx = click.get_current_context()
    if ctx.params.get('fast'):
        base += ['-f', FAST_COMPOSE_FILE]
    elif os.getenv('TEST'):
        base += ['-f', TESTS_COMPOSE_FILE]

    env = os.environ.copy()
    env['FORCAD_VERSION'] = VERSION
    run_command(
        base + args,
        cwd=BASE_DIR,
        env=env,
    )


def parse_host_data(value: str, default_port: int) -> Tuple[str, int]:
    if ':' in value:
        host, port = value.split(':', 1)
        port = int(port)
        return host, port
    return value, default_port


def print_file_exception_info(_func, path, _exc_info):
    print(f'File {path} not found')


def with_fast_option(func):
    @click.option(
        '--fast',
        is_flag=True,
        help='Use faster build with prebuilt images',
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

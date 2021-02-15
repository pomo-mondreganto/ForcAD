import os
import secrets
import shutil
import subprocess
import sys
import time
from typing import List, Tuple, Dict

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


def backup_config():
    backup_path = BASE_DIR / f'config_backup_{int(time.time())}.yml'
    shutil.copy2(CONFIG_PATH, backup_path)


def dump_config(config):
    with CONFIG_PATH.open(mode='w') as f:
        yaml.safe_dump(config, f)


def override_config(
        config, *,
        redis: str = None,
        database: str = None,
        rabbitmq: str = None):
    # patch config host variables to connect to the right place
    if redis:
        host, port = parse_host_data(redis, 6379)
        config['storages']['redis']['host'] = host
        config['storages']['redis']['port'] = port

    if database:
        host, port = parse_host_data(database, 5432)
        config['storages']['db']['host'] = host
        config['storages']['db']['port'] = port

    if rabbitmq:
        host, port = parse_host_data(rabbitmq, 5672)
        config['storages']['rabbitmq']['host'] = host
        config['storages']['rabbitmq']['port'] = port


def setup_auxiliary_structure(config):
    if 'admin' not in config:
        new_username = 'forcad'
        new_password = secrets.token_hex(8)
        config['admin'] = {
            'username': new_username,
            'password': new_password,
        }

        click.echo(f'Created new admin credentials: {new_username}:{new_password}')

    username = config['admin']['username']
    password = config['admin']['password']

    config['storages'] = {
        'db': {
            'host': 'postgres',
            'port': 5432,
            'dbname': 'forcad',
            'user': username,
            'password': password,
        },
        'rabbitmq': {
            'host': 'rabbitmq',
            'port': 5672,
            'vhost': 'forcad',
            'user': username,
            'password': password,
        },
        'redis': {
            'host': 'redis',
            'port': 6379,
            'db': 0,
            'password': password,
        },
    }


def run_command(command: List[str], cwd=None, env=None):
    p = subprocess.Popen(command, cwd=cwd, env=env)
    rc = p.wait()
    if rc != 0:
        print('[-] Failed!')
        sys.exit(1)


def get_output(command: List[str], cwd=None, env=None) -> str:
    return subprocess.check_output(command, cwd=cwd, env=env).decode()


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


def dump_tf_config(data: Dict[str, str]) -> str:
    return '\n'.join(f'{name} = "{value}"' for name, value in data.items())

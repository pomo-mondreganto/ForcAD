import os
import secrets
import shutil
import subprocess
import sys
import time
from typing import List, Tuple

import click
import yaml
from pydantic import ValidationError

from . import constants, models


def load_basic_config() -> models.BasicConfig:
    print_bold(f'Loading basic configuration from {constants.CONFIG_PATH}')
    with constants.CONFIG_PATH.open(mode='r') as f:
        raw = yaml.safe_load(f)

    # earlier this setting was called "global", so to make old configs work...
    if 'global' in raw:
        raw['game'] = raw.pop('global')

    try:
        config = models.BasicConfig.parse_obj(raw)
    except ValidationError as e:
        print_error(f'Invalid configuration file: {e}')
        sys.exit(1)

    return config


def load_config() -> models.Config:
    print_bold(f'Loading full configuration from {constants.CONFIG_PATH}')
    with constants.CONFIG_PATH.open(mode='r') as f:
        raw = yaml.safe_load(f)

    # earlier this setting was called "global", so to make old configs work...
    if 'global' in raw:
        raw['game'] = raw.pop('global')

    try:
        config = models.Config.parse_obj(raw)
    except ValidationError as e:
        print_error(f'Invalid configuration file: {e}')
        sys.exit(1)

    return config


def backup_config():
    backup_path = constants.BASE_DIR / f'config_backup_{int(time.time())}.yml'
    print_bold(f'Creating config backup at {backup_path}')
    shutil.copy2(constants.CONFIG_PATH, backup_path)


def dump_config(config: models.Config):
    with constants.CONFIG_PATH.open(mode='w') as f:
        yaml.safe_dump(config.dict(by_alias=True), f)


def override_config(
        config: models.Config, *,
        redis: str = None,
        database: str = None,
        rabbitmq: str = None):
    # patch config host variables to connect to the right place
    if redis:
        host, port = parse_host_data(redis, 6379)
        config.storages.redis.host = host
        config.storages.redis.port = port

    if database:
        host, port = parse_host_data(database, 5432)
        config.storages.db.host = host
        config.storages.db.port = port

    if rabbitmq:
        host, port = parse_host_data(rabbitmq, 5672)
        config.storages.rabbitmq.host = host
        config.storages.rabbitmq.port = port


def setup_auxiliary_structure(config: models.BasicConfig) -> models.Config:
    if not config.admin:
        new_username = constants.ADMIN_USER
        new_password = secrets.token_hex(8)
        config.admin = models.AdminConfig(
            username=new_username,
            password=new_password,
        )

        print_bold(f'Created new admin credentials: {new_username}:{new_password}')
    else:
        print_bold('Using existing credentials specified in admin section')

    username = config.admin.username
    password = config.admin.password

    storages = models.StoragesConfig(
        db=models.DatabaseConfig(user=username, password=password),
        rabbitmq=models.RabbitMQConfig(user=username, password=password),
        redis=models.RedisConfig(password=password),
    )

    return models.Config(
        admin=config.admin,
        game=config.game,
        storages=storages,
        tasks=config.tasks,
        teams=config.teams,
    )


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
        '-f', constants.BASE_COMPOSE_FILE,
    ]

    ctx = click.get_current_context()
    if ctx.params.get('fast'):
        base += ['-f', constants.FAST_COMPOSE_FILE]
    elif os.getenv('TEST'):
        base += ['-f', constants.TESTS_COMPOSE_FILE]

    env = os.environ.copy()
    env['FORCAD_VERSION'] = constants.VERSION
    run_command(
        base + args,
        cwd=constants.BASE_DIR,
        env=env,
    )


def parse_host_data(value: str, default_port: int) -> Tuple[str, int]:
    if ':' in value:
        host, port = value.split(':', 1)
        port = int(port)
        return host, port
    return value, default_port


def print_file_exception_info(_func, path, _exc_info):
    print_bold(f'File {path} not found')


def print_error(message: str):
    click.secho(message, fg='red')


def print_success(message: str):
    click.secho(message, fg='green')


def print_bold(message: str):
    click.secho(message, bold=True)

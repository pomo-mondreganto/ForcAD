#!/usr/bin/env python3

import shlex
import traceback

import argparse
import os
import shutil
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Tuple, List

BASE_DIR = Path(__file__).absolute().resolve().parent
CONFIG_DIR = BASE_DIR / 'backend' / 'config'
DOCKER_COMPOSE_FILE = 'docker-compose.yml'
BASE_COMPOSE_FILE = 'docker-compose-base.yml'

FULL_COMPOSE_PATH = BASE_DIR / 'docker-compose.yml'
VERSION = 'latest'

CONFIG_FILENAME = 'config.yml'

if os.environ.get('TEST'):
    CONFIG_FILENAME = 'test_config.yml'
elif os.environ.get('LOCAL'):
    CONFIG_FILENAME = 'local_config.yml'


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
        '-f', DOCKER_COMPOSE_FILE,
    ]
    env = os.environ.copy()
    env['FORCAD_VERSION'] = VERSION
    run_command(
        base + args,
        cwd=BASE_DIR,
        env=env
    )


def parse_host_data(value: str, default_port: int) -> Tuple[str, int]:
    if ':' in value:
        host, port = value.split(':', 1)
        port = int(port)
        return host, port
    return value, default_port


def setup_db(config):
    postgres_env_path = BASE_DIR.joinpath(
        'docker_config',
        'postgres',
        'environment.env',
    )

    db_config = config['storages']['db']
    host = db_config['host']
    port = db_config['port']
    user = db_config['user']
    password = db_config['password']
    db = db_config['dbname']

    postgres_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'POSTGRES_HOST={host}',
        f'POSTGRES_PORT={port}',
        f'POSTGRES_USER={user}',
        f'POSTGRES_PASSWORD={password}',
        f'POSTGRES_DB={db}',
    ]

    postgres_env_path.write_text('\n'.join(postgres_config))


def setup_redis(config):
    redis_env_path = BASE_DIR.joinpath(
        'docker_config',
        'redis',
        'environment.env',
    )

    redis_config = config['storages']['redis']
    host = redis_config.get('host', 'redis')
    port = redis_config.get('port', 6379)
    password = redis_config.get('password', None)

    redis_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'REDIS_HOST={host}',
        f'REDIS_PORT={port}',
        f'REDIS_PASSWORD={password}',
    ]

    redis_env_path.write_text('\n'.join(redis_config))


def setup_flower(config):
    flower_env_path = BASE_DIR.joinpath(
        'docker_config',
        'celery',
        'flower.env',
    )

    admin_config = config['admin']
    flower_username = admin_config['username']
    flower_password = admin_config['password']
    flower_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'FLOWER_BASIC_AUTH={flower_username}:{flower_password}',
    ]

    flower_env_path.write_text('\n'.join(flower_config))


def setup_rabbitmq(config):
    rabbitmq_env_path = BASE_DIR.joinpath(
        'docker_config',
        'rabbitmq',
        'environment.env',
    )

    rabbitmq_config = config['storages']['rabbitmq']
    host = rabbitmq_config.get('host', 'rabbitmq')
    port = rabbitmq_config.get('port', 5672)
    user = rabbitmq_config['user']
    password = rabbitmq_config['password']
    vhost = rabbitmq_config['vhost']

    rabbitmq_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'RABBITMQ_HOST={host}',
        f'RABBITMQ_PORT={port}',
        f'RABBITMQ_DEFAULT_USER={user}',
        f'RABBITMQ_DEFAULT_PASS={password}',
        f'RABBITMQ_DEFAULT_VHOST={vhost}',
    ]

    rabbitmq_env_path.write_text('\n'.join(rabbitmq_config))


def setup_admin_api(config):
    admin_api_env_path = BASE_DIR.joinpath(
        'docker_config',
        'services',
        'admin.env',
    )

    admin_config = config['admin']
    username = admin_config['username']
    password = admin_config['password']

    admin_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'ADMIN_USERNAME={username}',
        f'ADMIN_PASSWORD={password}',
    ]

    admin_api_env_path.write_text('\n'.join(admin_config))


def prepare_docker_compose(args):
    base_conf = yaml.safe_load(FULL_COMPOSE_PATH.open(mode='r'))

    if not os.environ.get('TEST'):
        if 'redis' in args and args.redis:
            del base_conf['services']['redis']

        if 'database' in args and args.database:
            del base_conf['services']['postgres']

    res_path = BASE_DIR / 'docker-compose-base.yml'
    with res_path.open(mode='w') as f:
        yaml.dump(base_conf, f)


def setup_config(args):
    override_config(args)
    conf_path = CONFIG_DIR / CONFIG_FILENAME
    config = yaml.safe_load(conf_path.open(mode='r'))
    setup_db(config)
    setup_redis(config)
    setup_flower(config)
    setup_rabbitmq(config)
    setup_admin_api(config)
    prepare_docker_compose(args)


def override_config(args):
    conf_path = CONFIG_DIR / CONFIG_FILENAME
    config = yaml.safe_load(conf_path.open(mode='r'))

    # create config backup
    backup_path = CONFIG_DIR / f'config_backup_{int(time.time())}.yml'
    shutil.copy2(conf_path, backup_path)

    # patch config host variables to connect to the right place
    if 'redis' in args and args.redis:
        host, port = parse_host_data(args.redis, 6379)
        config['storages']['redis']['host'] = host
        config['storages']['redis']['port'] = port

    if 'database' in args and args.database:
        host, port = parse_host_data(args.database, 5432)
        config['storages']['db']['host'] = host
        config['storages']['db']['port'] = port

    if 'rabbitmq' in args and args.rabbitmq:
        host, port = parse_host_data(args.rabbitmq, 5672)
        config['storages']['rabbitmq']['host'] = host
        config['storages']['rabbitmq']['port'] = port

    with conf_path.open(mode='w') as f:
        yaml.safe_dump(config, f)


def print_tokens(_args):
    command = [
        'docker-compose',
        '-f', FULL_COMPOSE_PATH,
        'exec', '-T', 'client_api',
        'python3', '/app/scripts/print_tokens.py',
    ]
    res = subprocess.check_output(
        command,
        cwd=BASE_DIR,
    )

    print(res.decode().strip())


def print_file_exception_info(_func, path, _exc_info):
    print(f'File {path} not found')


def reset_game(_args):
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


def build(_args):
    run_docker(['build'])


def start_game(args):
    run_docker(['up', '--build', '-d', '--scale', f'celery={args.instances}'])


def scale_celery(args):
    run_docker([
        'up', '-d', '--no-recreate', '--no-build',
        '--scale', f'celery={args.instances}',
        'celery',
    ])


def run_worker(args):
    # patch configuration
    override_config(args)
    setup_config(args)

    run_docker([
        'up', '--build', '-d',
        '--scale', f'celery={args.instances}',
        'celery',
    ])


def pause_game(_args):
    run_docker(['stop', 'celerybeat', 'tcp_receiver'])


def resume_game(_args):
    run_docker(['start', 'celerybeat', 'tcp_receiver'])


def run_docker_command(args):
    run_docker(shlex.split(args.command))


def run_flake(_args):
    command = [
        'flake8',
        '--ignore', 'E402',
        'control.py', 'backend',
    ]
    run_command(command, cwd=BASE_DIR)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control ForcAD')
    subparsers = parser.add_subparsers()

    setup_parser = subparsers.add_parser(
        'setup',
        help='Transfer centralized config to environment files, '
             'prepare base docker-compose file',
    )
    setup_parser.set_defaults(func=setup_config)
    setup_parser.add_argument('--redis', type=str,
                              help='External redis address '
                                   '(disables built-in redis container)',
                              required=False)
    setup_parser.add_argument('--database', type=str,
                              help='External postgres address '
                                   '(disables built-in postgres container)',
                              required=False)

    print_tokens_parser = subparsers.add_parser(
        'print_tokens',
        help='Print team tokens',
    )
    print_tokens_parser.set_defaults(func=print_tokens)

    reset_parser = subparsers.add_parser(
        'reset',
        help='Reset the game & cleanup',
    )
    reset_parser.set_defaults(func=reset_game)
    reset_parser.add_argument('-f', '--fast', action='store_true',
                              help='Use faster build compose file')

    build_parser = subparsers.add_parser(
        'build',
        help='Build the images, don\'t run',
    )
    build_parser.set_defaults(func=build)
    build_parser.add_argument('-f', '--fast', action='store_true',
                              help='Use faster build with prebuilt images')

    start_parser = subparsers.add_parser(
        'start',
        help='Start the forcad, building if necessary (with cache)',
    )
    start_parser.set_defaults(func=start_game)
    start_parser.add_argument('-f', '--fast', action='store_true',
                              help='Use faster build with prebuilt images')
    start_parser.add_argument('-i', '--instances', type=int, metavar='N',
                              default=1,
                              help='Number of celery worker instances',
                              required=False)

    scale_celery_parser = subparsers.add_parser(
        'scale_celery',
        help='Scale the number of celery worker containers',
    )
    scale_celery_parser.set_defaults(func=scale_celery)
    scale_celery_parser.add_argument('-i', '--instances', type=int,
                                     metavar='N',
                                     help='Number of celery worker instances',
                                     required=True)

    worker_parser = subparsers.add_parser(
        'worker',
        help='Start the celery workers only',
    )
    worker_parser.set_defaults(func=run_worker)
    worker_parser.add_argument('-i', '--instances', type=int, metavar='N',
                               default=1,
                               help='Number of celery worker instances',
                               required=False)
    worker_parser.add_argument('-f', '--fast', action='store_true',
                               help='Use faster build with prebuilt images')
    worker_parser.add_argument('--redis', type=str,
                               help='Redis address for the worker to connect',
                               required=True)
    worker_parser.add_argument('--rabbitmq', type=str,
                               help='RabbitMQ address for the worker',
                               required=True)
    worker_parser.add_argument('--database', type=str,
                               help='Postgres address for the worker',
                               required=True)

    pause_game_parser = subparsers.add_parser(
        'pause_game',
        help='Stop updating rounds & receiving flags',
    )
    pause_game_parser.set_defaults(func=pause_game)

    resume_game_parser = subparsers.add_parser(
        'resume_game',
        help='Start updating rounds & receiving flags '
             '(counterpart of pause_game command)',
    )
    resume_game_parser.set_defaults(func=resume_game)

    run_docker_parser = subparsers.add_parser(
        'rd',
        help='Run docker-compose command with correct compose files',
    )
    run_docker_parser.set_defaults(func=run_docker_command)
    run_docker_parser.add_argument(
        '-f', '--fast',
        action='store_true',
        help='Use faster build with prebuilt images',
    )
    run_docker_parser.add_argument(
        '-c', '--command',
        type=str,
        help='Docker-compose arguments (e.g. "logs -f --tail 200")',
    )

    flake_parser = subparsers.add_parser(
        'flake',
        help='Run flake8 validation',
    )
    flake_parser.set_defaults(func=run_flake)

    parsed = parser.parse_args()

    if ('fast' in parsed and parsed.fast) or os.environ.get('FAST'):
        DOCKER_COMPOSE_FILE = 'docker-compose-fast.yml'
    elif os.environ.get('TEST'):
        DOCKER_COMPOSE_FILE = 'docker-compose-tests.yml'

    version_path = BASE_DIR / '.version'
    try:
        VERSION = version_path.read_text().strip()
    except FileNotFoundError:
        pass

    try:
        parsed.func(parsed)
    except Exception as e:
        tb = traceback.format_exc()
        print('Got exception:', e, tb)
        sys.exit(1)

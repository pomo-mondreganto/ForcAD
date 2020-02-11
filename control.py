#!/usr/bin/env python3

import os
import traceback

import argparse
import shutil
import subprocess
import time
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'backend', 'config')
DOCKER_COMPOSE_FILE = 'docker-compose.yml'

CONFIG_FILENAME = 'config.yml'

if os.environ.get('TEST'):
    CONFIG_FILENAME = 'test_config.yml'
elif os.environ.get('LOCAL'):
    CONFIG_FILENAME = 'local_config.yml'


def run_command(command, cwd=None, env=None):
    p = subprocess.Popen(command, cwd=cwd, env=env)
    rc = p.wait()
    if rc != 0:
        print('[-] Failed!')
        exit(1)


def setup_db(config):
    postgres_env_path = os.path.join(
        BASE_DIR,
        'docker_config',
        'postgres',
        'environment.env',
    )
    db_config = config['storages']['db']
    postgres_host = db_config['host']
    postgres_port = db_config['port']
    postgres_user = db_config['user']
    postgres_password = db_config['password']
    postgres_db = db_config['dbname']

    postgres_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        'POSTGRES_HOST={postgres_host}'.format(postgres_host=postgres_host),
        'POSTGRES_PORT={postgres_port}'.format(postgres_port=postgres_port),
        'POSTGRES_USER={postgres_user}'.format(postgres_user=postgres_user),
        'POSTGRES_PASSWORD={postgres_password}'.format(postgres_password=postgres_password),
        'POSTGRES_DB={postgres_db}'.format(postgres_db=postgres_db),
    ]

    with open(postgres_env_path, 'w') as f:
        f.write('\n'.join(postgres_config))


def setup_redis(config):
    redis_env_path = os.path.join(
        BASE_DIR,
        'docker_config',
        'redis',
        'environment.env',
    )

    redis_pass = config['storages']['redis'].get('password', None)

    redis_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        'REDIS_PASSWORD={redis_pass}'.format(redis_pass=redis_pass),
    ]

    with open(redis_env_path, 'w') as f:
        f.write('\n'.join(redis_config))


def setup_flower(config):
    flower_env_path = os.path.join(
        BASE_DIR,
        'docker_config',
        'celery',
        'flower_environment.env',
    )

    flower_username = config['flower']['username']
    flower_password = config['flower']['password']
    flower_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        'FLOWER_BASIC_AUTH={flower_username}:{flower_password}'.format(
            flower_username=flower_username,
            flower_password=flower_password,
        ),
    ]

    with open(flower_env_path, 'w') as f:
        f.write('\n'.join(flower_config))


def setup_rabbitmq(config):
    rabbitmq_env_path = os.path.join(
        BASE_DIR,
        'docker_config',
        'rabbitmq',
        'environment.env',
    )

    rabbitmq_config = config['storages']['rabbitmq']
    user = rabbitmq_config['user']
    password = rabbitmq_config['password']
    vhost = rabbitmq_config['vhost']
    config_data = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        'RABBITMQ_DEFAULT_USER={user}'.format(user=user),
        'RABBITMQ_DEFAULT_PASS={password}'.format(password=password),
        'RABBITMQ_DEFAULT_VHOST={vhost}'.format(vhost=vhost),
    ]

    with open(rabbitmq_env_path, 'w') as f:
        f.write('\n'.join(config_data))


def setup_config(*_args, **_kwargs):
    conf_path = os.path.join(CONFIG_DIR, CONFIG_FILENAME)
    config = yaml.load(open(conf_path), Loader=yaml.FullLoader)
    setup_db(config)
    setup_redis(config)
    setup_flower(config)
    setup_rabbitmq(config)


def setup_worker(redis, database):
    conf_path = os.path.join(CONFIG_DIR, CONFIG_FILENAME)
    config = yaml.load(open(conf_path), Loader=yaml.FullLoader)

    # create config backup
    backup_path = os.path.join(CONFIG_DIR, f'config_backup_{int(time.time())}.yml')
    with open(backup_path, 'w') as f:
        yaml.dump(config, f)

    # patch config host variables to connect to the right place
    config['storages']['redis']['host'] = redis
    config['storages']['db']['host'] = database

    with open(conf_path, 'w') as f:
        yaml.dump(config, f)

    setup_config()


def print_tokens(*_args, **_kwargs):
    res = subprocess.check_output(
        ['docker-compose', '-f', DOCKER_COMPOSE_FILE, 'exec', 'webapi', 'python3', '/app/scripts/print_tokens.py'],
        cwd=BASE_DIR,
    )

    print(res.decode().strip())


def print_file_exception_info(_func, path, _exc_info):
    print(f'File {path} not found')


def reset_game(*_args, **_kwargs):
    data_path = os.path.join(BASE_DIR, 'docker_volumes/postgres/data')
    shutil.rmtree(data_path, onerror=print_file_exception_info)

    run_command(
        ['docker-compose', '-f', DOCKER_COMPOSE_FILE, 'down', '-v', '--remove-orphans'],
        cwd=BASE_DIR,
    )


def build(*_args, **_kwargs):
    run_command(
        ['docker-compose', '-f', DOCKER_COMPOSE_FILE, 'build'],
        cwd=BASE_DIR,
    )


def start_game(*_args, **_kwargs):
    run_command(
        ['docker-compose', '-f', DOCKER_COMPOSE_FILE, 'up', '--build', '-d'],
        cwd=BASE_DIR,
    )


def scale_celery(instances, *_args, **_kwargs):
    if instances is None:
        print('Please, specify number of instances (-i N)')
        exit(1)

    run_command(
        [
            'docker-compose',
            '-f', DOCKER_COMPOSE_FILE,
            'up', '-d',
            '--no-recreate',
            '--no-build',
            '--scale', f'celery={instances}',
            'celery',
        ],
        cwd=BASE_DIR,
    )


def run_worker(redis, database, *_args, **_kwargs):
    if redis is None or database is None:
        print('Please, specify redis & database address --redis IP, --database IP')
        exit(1)

    # patch configuration
    setup_worker(redis, database)

    run_command(
        ['docker-compose', '-f', DOCKER_COMPOSE_FILE, 'up', '--build', '-d', 'celery'],
        cwd=BASE_DIR,
    )


COMMANDS = {
    'setup': setup_config,
    'print_tokens': print_tokens,
    'reset': reset_game,
    'build': build,
    'start': start_game,
    'scale_celery': scale_celery,
    'worker': run_worker,
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control ForcAD')
    parser.add_argument('command', choices=COMMANDS.keys(), help='Command to run')
    parser.add_argument('--fast', action='store_true', help='Use faster build with default source code')
    parser.add_argument('-i', '--instances', type=int, metavar='N', help='Number of celery instances for scale_celery')
    parser.add_argument('--redis', type=str, help='Redis address for the worker to connect')
    parser.add_argument('--database', type=str, help='PostgreSQL address for the worker to connect')

    args = parser.parse_args()

    if args.fast:
        DOCKER_COMPOSE_FILE = 'docker-compose-fast.yml'
    elif os.environ.get('TEST'):
        DOCKER_COMPOSE_FILE = 'docker-compose-tests.yml'

    try:
        COMMANDS[args.command](**vars(args))
    except Exception as e:
        tb = traceback.format_exc()
        print('Got exception:', e, tb)
        exit(1)

#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess

import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'backend', 'config')


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


def setup_config(*_args, **_kwargs):
    conf_path = os.path.join(CONFIG_DIR, 'config.yml')
    config = yaml.load(open(conf_path), Loader=yaml.FullLoader)
    setup_db(config)
    setup_flower(config)


def print_tokens(*_args, **_kwargs):
    res = subprocess.check_output(
        ['docker-compose', 'exec', 'webapi', 'python3', '/app/scripts/print_tokens.py'],
        cwd=BASE_DIR,
    )

    print(res.decode().strip())


def print_file_exception_info(_func, path, _exc_info):
    print(f'File {path} not found')


def reset_game(*_args, **_kwargs):
    data_path = os.path.join(BASE_DIR, 'docker_volumes/postgres/data')
    shutil.rmtree(data_path, onerror=print_file_exception_info)

    subprocess.check_output(
        ['docker-compose', 'down', '-v', '--remove-orphans'],
        cwd=BASE_DIR,
    )


def scale_celery(instances, *_args, **_kwargs):
    if instances is None:
        print('Please, specify number of instances (-i N)')
        exit(1)

    subprocess.check_output(
        ['docker-compose', 'up', '--scale', f'celery={instances}', '-d'],
        cwd=BASE_DIR,
    )


COMMANDS = {
    'setup': setup_config,
    'print_tokens': print_tokens,
    'reset': reset_game,
    'scale_celery': scale_celery,
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control ForcAD')
    parser.add_argument('command', choices=COMMANDS.keys(), help='Command to run')
    parser.add_argument('-i', '--instances', type=int, metavar='N', help='Number of celery instances for scale_celery')
    args = parser.parse_args()

    try:
        COMMANDS[args.command](**vars(args))
    except Exception as e:
        print('Got exception:', e)

#!/usr/bin/env python3

import os

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
        "# THIS FILE IS MANAGED BY 'setup_config'",
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
        "# THIS FILE IS MANAGED BY 'setup_config'",
        'FLOWER_BASIC_AUTH={flower_username}:{flower_password}'.format(
            flower_username=flower_username,
            flower_password=flower_password,
        ),
    ]

    with open(flower_env_path, 'w') as f:
        f.write('\n'.join(flower_config))


def run():
    conf_path = os.path.join(CONFIG_DIR, 'config.yml')
    config = yaml.load(open(conf_path), Loader=yaml.FullLoader)
    setup_db(config)
    setup_flower(config)


if __name__ == '__main__':
    run()

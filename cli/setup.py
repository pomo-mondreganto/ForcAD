import shutil
import time

import click
import yaml

from . import utils
from .constants import BASE_DIR, CONFIG_PATH, FULL_COMPOSE_PATH, BASE_COMPOSE_FILE


@click.command(help='Initialize ForcAD configuration')
@click.option(
    '--redis',
    metavar='ADDR',
    help='External redis address (disables built-in redis container)',
)
@click.option(
    '--database',
    metavar='ADDR',
    help='External Postgres address (disables built-in postgres container)',
)
@click.option(
    '--rabbitmq',
    metavar='ADDR',
    help='External RabbitMQ address (disables built-in rabbitmq container)',
)
def setup(redis, database, rabbitmq, **_kwargs):
    override_config(redis=redis, database=database, rabbitmq=rabbitmq)
    config = utils.load_config()
    setup_db(config)
    setup_redis(config)
    setup_flower(config)
    setup_rabbitmq(config)
    setup_admin_api(config)
    prepare_compose(redis=redis, database=database, rabbitmq=rabbitmq)


def override_config(redis: str = None, database: str = None, rabbitmq: str = None):
    config = utils.load_config()

    # create config backup
    backup_path = BASE_DIR / f'config_backup_{int(time.time())}.yml'
    shutil.copy2(CONFIG_PATH, backup_path)

    # patch config host variables to connect to the right place
    if redis:
        host, port = utils.parse_host_data(redis, 6379)
        config['storages']['redis']['host'] = host
        config['storages']['redis']['port'] = port

    if database:
        host, port = utils.parse_host_data(database, 5432)
        config['storages']['db']['host'] = host
        config['storages']['db']['port'] = port

    if rabbitmq:
        host, port = utils.parse_host_data(rabbitmq, 5672)
        config['storages']['rabbitmq']['host'] = host
        config['storages']['rabbitmq']['port'] = port

    with CONFIG_PATH.open(mode='w') as f:
        yaml.safe_dump(config, f)


def setup_db(config):
    postgres_env_path = BASE_DIR.joinpath(
        'docker_config',
        'postgres_environment.env',
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
        'redis_environment.env',
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
        'rabbitmq_environment.env',
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


def prepare_compose(redis: str = None, database: str = None, rabbitmq: str = None):
    base_conf = yaml.safe_load(FULL_COMPOSE_PATH.open(mode='r'))

    if redis:
        del base_conf['services']['redis']

    if database:
        del base_conf['services']['postgres']

    if rabbitmq:
        del base_conf['services']['rabbitmq']

    res_path = BASE_DIR / BASE_COMPOSE_FILE
    with res_path.open(mode='w') as f:
        yaml.dump(base_conf, f)

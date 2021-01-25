import click
import yaml

from cli import utils
from cli.base.setup import override_config
from cli.constants import SECRETS_DIR, KUSTOMIZATION_BASE_PATH, KUSTOMIZATION_PATH
from .utils import write_secret


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
    setup_postgres_secret(config)
    setup_rabbitmq_secret(config)
    setup_redis_secret(config)
    setup_admin_secret(config)
    prepare_kustomize(redis=redis, database=database, rabbitmq=rabbitmq)


def setup_postgres_secret(config):
    path = SECRETS_DIR / 'postgres.yml'
    name = 'forcad-postgres-secret'

    db_config = config['storages']['db']
    data = {
        'POSTGRES_HOST': db_config['host'],
        'POSTGRES_PORT': db_config['port'],
        'POSTGRES_USER': db_config['user'],
        'POSTGRES_PASSWORD': db_config['password'],
        'POSTGRES_DB': db_config['dbname'],
    }

    write_secret(name=name, path=path, data=data)


def setup_rabbitmq_secret(config):
    path = SECRETS_DIR / 'rabbitmq.yml'
    name = 'forcad-rabbitmq-secret'

    rabbitmq_config = config['storages']['rabbitmq']
    data = {
        'RABBITMQ_HOST': rabbitmq_config.get('host', 'rabbitmq'),
        'RABBITMQ_PORT': rabbitmq_config.get('port', 5672),
        'RABBITMQ_DEFAULT_USER': rabbitmq_config['user'],
        'RABBITMQ_DEFAULT_PASS': rabbitmq_config['password'],
        'RABBITMQ_DEFAULT_VHOST': rabbitmq_config['vhost'],
    }

    write_secret(name=name, path=path, data=data)


def setup_redis_secret(config):
    path = SECRETS_DIR / 'redis.yml'
    name = 'forcad-redis-secret'

    redis_config = config['storages']['redis']
    data = {
        'REDIS_HOST': redis_config.get('host', 'redis'),
        'REDIS_PORT': redis_config.get('port', 6379),
        'REDIS_PASSWORD': redis_config.get('password', None),
    }

    write_secret(name=name, path=path, data=data)


def setup_admin_secret(config):
    path = SECRETS_DIR / 'admin.yml'
    name = 'forcad-admin-secret'

    admin_config = config['admin']
    data = {
        'ADMIN_USERNAME': admin_config['username'],
        'ADMIN_PASSWORD': admin_config['password'],
    }

    write_secret(name=name, path=path, data=data)


def prepare_kustomize(redis: str = None, database: str = None, rabbitmq: str = None):
    with KUSTOMIZATION_BASE_PATH.open(mode='r') as f:
        base_conf = yaml.safe_load(f)

    if redis:
        base_conf['resources'].remove('config/redis.yml')
    if database:
        base_conf['resources'].remove('config/postgres.yml')
    if rabbitmq:
        base_conf['resources'].remove('config/rabbitmq.yml')

    with KUSTOMIZATION_PATH.open(mode='w') as f:
        yaml.safe_dump(base_conf, f)

import click
import yaml

from cli import utils, constants, models
from cli.kube.validate import validate
from cli.options import with_external_services_option
from .utils import write_secret


@click.command(help='Initialize ForcAD configuration for custom cluster deploy')
@with_external_services_option
@click.pass_context
def setup(ctx: click.Context, redis, database, rabbitmq, **_kwargs):
    ctx.invoke(validate, full=False)
    raw_config = utils.load_basic_config()
    basic_config = models.BasicConfig.parse_obj(raw_config)
    config = utils.setup_auxiliary_structure(basic_config)

    utils.override_config(config, redis=redis, database=database, rabbitmq=rabbitmq)
    utils.backup_config()
    utils.dump_config(config)

    setup_postgres_secret(config.storages.db)
    setup_rabbitmq_secret(config.storages.rabbitmq)
    setup_redis_secret(config.storages.redis)
    setup_admin_secret(config.admin)
    setup_config_file_secret()

    prepare_kustomize(redis=redis, database=database, rabbitmq=rabbitmq)


def setup_postgres_secret(config: models.DatabaseConfig):
    name = 'forcad-postgres-secret'

    data = {
        'POSTGRES_HOST': config.host,
        'POSTGRES_PORT': config.port,
        'POSTGRES_USER': config.user,
        'POSTGRES_PASSWORD': config.password,
        'POSTGRES_DB': config.dbname,
    }

    write_secret(name=name, path=constants.POSTGRES_SECRET_PATH, data=data)


def setup_rabbitmq_secret(config: models.RabbitMQConfig):
    name = 'forcad-rabbitmq-secret'

    data = {
        'RABBITMQ_HOST': config.host,
        'RABBITMQ_PORT': config.port,
        'RABBITMQ_DEFAULT_USER': config.user,
        'RABBITMQ_DEFAULT_PASS': config.password,
        'RABBITMQ_DEFAULT_VHOST': config.vhost,
    }

    write_secret(name=name, path=constants.RABBITMQ_SECRET_PATH, data=data)


def setup_redis_secret(config: models.RedisConfig):
    name = 'forcad-redis-secret'

    data = {
        'REDIS_HOST': config.host,
        'REDIS_PORT': config.port,
        'REDIS_PASSWORD': config.password,
    }

    write_secret(name=name, path=constants.REDIS_SECRET_PATH, data=data)


def setup_admin_secret(config: models.AdminConfig):
    name = 'forcad-admin-secret'

    data = {
        'ADMIN_USERNAME': config.username,
        'ADMIN_PASSWORD': config.password,
    }

    write_secret(name=name, path=constants.ADMIN_SECRET_PATH, data=data)


def setup_config_file_secret():
    content = constants.CONFIG_PATH.read_text()
    name = 'forcad-config-file'
    data = {'content': content}
    write_secret(name=name, path=constants.CONFIG_SECRET_PATH, data=data)


def prepare_kustomize(redis: str = None, database: str = None, rabbitmq: str = None):
    with constants.KUSTOMIZATION_BASE_PATH.open(mode='r') as f:
        base_conf = yaml.safe_load(f)

    if redis:
        base_conf['resources'].remove('config/redis.yml')
    if database:
        base_conf['resources'].remove('config/postgres.yml')
    if rabbitmq:
        base_conf['resources'].remove('config/rabbitmq.yml')

    with constants.KUSTOMIZATION_PATH.open(mode='w') as f:
        yaml.safe_dump(base_conf, f)

import click
import yaml

from cli import utils, constants, models
from cli.options import with_external_services_option


@click.command(help='Initialize ForcAD configuration')
@with_external_services_option
def setup(redis, database, rabbitmq, **_kwargs):
    utils.backup_config()

    basic_config = utils.load_basic_config()
    config = utils.setup_auxiliary_structure(basic_config)
    utils.override_config(config, redis=redis, database=database, rabbitmq=rabbitmq)

    utils.dump_config(config)

    setup_db(config.storages.db)
    setup_redis(config.storages.redis)
    setup_rabbitmq(config.storages.rabbitmq)
    setup_admin_api(config.admin)

    prepare_compose(redis=redis, database=database, rabbitmq=rabbitmq)


def setup_db(config: models.DatabaseConfig):
    postgres_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'POSTGRES_HOST={config.host}',
        f'POSTGRES_PORT={config.port}',
        f'POSTGRES_USER={config.user}',
        f'POSTGRES_PASSWORD={config.password}',
        f'POSTGRES_DB={config.dbname}',
    ]

    utils.print_bold(f'Writing database env to {constants.POSTGRES_ENV_PATH}')
    constants.POSTGRES_ENV_PATH.write_text('\n'.join(postgres_config))


def setup_redis(config: models.RedisConfig):
    redis_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'REDIS_HOST={config.host}',
        f'REDIS_PORT={config.port}',
        f'REDIS_PASSWORD={config.password}',
    ]

    utils.print_bold(f'Writing redis env to {constants.REDIS_ENV_PATH}')
    constants.REDIS_ENV_PATH.write_text('\n'.join(redis_config))


def setup_rabbitmq(config: models.RabbitMQConfig):
    management_url = f'http://{config.user}:{config.password}@{config.host}:15672/api/'
    rabbitmq_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'RABBITMQ_HOST={config.host}',
        f'RABBITMQ_PORT={config.port}',
        f'RABBITMQ_DEFAULT_USER={config.user}',
        f'RABBITMQ_DEFAULT_PASS={config.password}',
        f'RABBITMQ_DEFAULT_VHOST={config.vhost}',
        f'BROKER_API_URL={management_url}',
    ]

    utils.print_bold(f'Writing broker env to {constants.RABBITMQ_ENV_PATH}')
    constants.RABBITMQ_ENV_PATH.write_text('\n'.join(rabbitmq_config))


def setup_admin_api(config: models.AdminConfig):
    admin_config = [
        "# THIS FILE IS MANAGED BY 'control.py'",
        f'ADMIN_USERNAME={config.username}',
        f'ADMIN_PASSWORD={config.password}',
    ]

    utils.print_bold(f'Writing admin env to {constants.ADMIN_ENV_PATH}')
    constants.ADMIN_ENV_PATH.write_text('\n'.join(admin_config))


def prepare_compose(redis: str = None, database: str = None, rabbitmq: str = None):
    with constants.FULL_COMPOSE_PATH.open(mode='r') as f:
        base_conf = yaml.safe_load(f)

    if redis:
        del base_conf['services']['redis']

    if database:
        del base_conf['services']['postgres']

    if rabbitmq:
        del base_conf['services']['rabbitmq']

    res_path = constants.BASE_DIR / constants.BASE_COMPOSE_FILE
    utils.print_bold(f'Writing generated compose base to {res_path}')
    with res_path.open(mode='w') as f:
        yaml.dump(base_conf, f)

import os

from lib import storage


def get_web_credentials() -> dict:
    return {
        'username': os.environ['ADMIN_USERNAME'],
        'password': os.environ['ADMIN_PASSWORD'],
    }


def get_redis_config() -> dict:
    return {
        'host': os.environ['REDIS_HOST'],
        'port': os.environ['REDIS_PORT'],
        'password': os.environ['REDIS_PASSWORD'],
        'db': 0,
    }


def get_db_config() -> dict:
    return {
        'host': os.environ['POSTGRES_HOST'],
        'port': os.environ['POSTGRES_PORT'],
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'dbname': os.environ['POSTGRES_DB']
    }


def get_broker_url() -> str:
    """Get broker url for RabbitMQ from config."""
    host = os.environ['RABBITMQ_HOST']
    user = os.environ['RABBITMQ_DEFAULT_USER']
    port = os.environ['RABBITMQ_PORT']
    password = os.environ['RABBITMQ_DEFAULT_PASS']
    vhost = os.environ['RABBITMQ_DEFAULT_VHOST']

    broker_url = f'amqp://{user}:{password}@{host}:{port}/{vhost}'
    return broker_url


def get_celery_config() -> dict:
    game_config = storage.game.get_current_global_config()

    host = os.environ['REDIS_HOST']
    port = os.environ['REDIS_PORT']
    password = os.environ['REDIS_PASSWORD']
    db = 1

    result_backend = f'redis://:{password}@{host}:{port}/{db}'

    broker_url = get_broker_url()

    conf = {
        'accept_content': ['pickle'],
        'broker_url': broker_url,
        'result_backend': result_backend,
        'result_serializer': 'pickle',
        'task_serializer': 'pickle',
        'timezone': game_config.timezone,
        'worker_prefetch_multiplier': 1,
    }

    return conf

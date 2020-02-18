import os

import storage


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
    """Get broker url for RabbitMQ from config"""
    amqp_host = os.environ['RABBITMQ_HOST']
    amqp_user = os.environ['RABBITMQ_DEFAULT_USER']
    amqp_port = os.environ['RABBITMQ_PORT']
    amqp_pass = os.environ['RABBITMQ_DEFAULT_PASS']
    amqp_vhost = os.environ['RABBITMQ_DEFAULT_VHOST']

    broker_url = f'amqp://{amqp_user}:{amqp_pass}@{amqp_host}:{amqp_port}/{amqp_vhost}'
    return broker_url


def get_celery_config() -> dict:
    game_config = storage.game.get_current_global_config()

    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_pass = os.environ['REDIS_PASSWORD']
    redis_db = 1

    result_backend = f'redis://:{redis_pass}@{redis_host}:{redis_port}/{redis_db}'

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

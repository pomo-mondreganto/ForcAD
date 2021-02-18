import os

from lib import storage
from . import models


def get_web_credentials() -> models.WebCredentials:
    return models.WebCredentials()


def get_redis_config() -> models.Redis:
    return models.Redis()


def get_db_config() -> models.Database:
    return models.Database()


def get_broker_url() -> str:
    """Get broker url for RabbitMQ from config."""
    host = os.environ['RABBITMQ_HOST']
    user = os.environ['RABBITMQ_DEFAULT_USER']
    port = os.environ['RABBITMQ_PORT']
    password = os.environ['RABBITMQ_DEFAULT_PASS']
    vhost = os.environ['RABBITMQ_DEFAULT_VHOST']

    broker_url = f'amqp://{user}:{password}@{host}:{port}/{vhost}'
    return broker_url


def get_celery_config() -> models.Celery:
    redis_config = get_redis_config()
    redis_config.db = 1
    return models.Celery(
        broker_url=get_broker_url(),
        result_backend=redis_config.url,
        timezone=storage.game.get_current_game_config().timezone,
    )

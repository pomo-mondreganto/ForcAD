import os
from typing import List

from pydantic import BaseModel, Field


def env_field(key: str) -> Field:
    return Field(default_factory=lambda: os.environ[key])


class Redis(BaseModel):
    host: str = env_field('REDIS_HOST')
    port: int = env_field('REDIS_PORT')
    password: str = env_field('REDIS_PASSWORD')
    db: int = 0

    @property
    def url(self) -> str:
        return f'redis://:{self.password}@{self.host}:{self.port}/{self.db}'


class WebCredentials(BaseModel):
    username: str = env_field('ADMIN_USERNAME')
    password: str = env_field('ADMIN_PASSWORD')


class Database(BaseModel):
    host: str = env_field('POSTGRES_HOST')
    port: int = env_field('POSTGRES_PORT')
    user: str = env_field('POSTGRES_USER')
    password: str = env_field('POSTGRES_PASSWORD')
    dbname: str = env_field('POSTGRES_DB')


class Celery(BaseModel):
    broker_url: str
    result_backend: str
    timezone: str

    worker_prefetch_multiplier: int = 1

    result_expires = 15 * 60
    redis_socket_timeout: int = 10
    redis_socket_keepalive: bool = True
    redis_retry_on_timeout: bool = True

    accept_content: List[str] = ['pickle', 'json']
    result_serializer: str = 'pickle'
    task_serializer: str = 'pickle'

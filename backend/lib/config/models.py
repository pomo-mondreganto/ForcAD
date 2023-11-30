from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Redis(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str
    port: int
    password: str
    db: int = 0

    @property
    def url(self) -> str:
        return f'redis://:{self.password}@{self.host}:{self.port}/{self.db}'


class WebCredentials(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='admin_')

    username: str
    password: str


class Database(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgres_')

    host: str
    port: int
    user: str
    password: str
    dbname: str = Field(validation_alias='postgres_db')


class Celery(BaseModel):
    broker_url: str
    result_backend: str
    timezone: str

    worker_prefetch_multiplier: int = 1

    result_expires: int = 15 * 60
    redis_socket_timeout: int = 10
    redis_socket_keepalive: bool = True
    redis_retry_on_timeout: bool = True

    accept_content: List[str] = ['pickle', 'json']
    result_serializer: str = 'pickle'
    task_serializer: str = 'pickle'

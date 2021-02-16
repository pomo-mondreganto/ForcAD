from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class AdminConfig(BaseModel):
    username: str
    password: str


class DatabaseConfig(BaseModel):
    user: str
    password: str
    host: str = 'postgres'
    port: int = 5432
    dbname: str = 'forcad'


class RabbitMQConfig(BaseModel):
    user: str
    password: str
    host: str = 'rabbitmq'
    port: int = 5672
    vhost: str = 'forcad'


class RedisConfig(BaseModel):
    password: str
    host: str = 'redis'
    port: int = 6379
    db: int = 0


class StoragesConfig(BaseModel):
    db: DatabaseConfig
    rabbitmq: RabbitMQConfig
    redis: RedisConfig


class GlobalConfig(BaseModel):
    flag_lifetime: int
    round_time: int
    start_time: datetime

    timezone: str = 'UTC'
    default_score: Union[int, float] = 2500
    game_hardness: Union[int, float] = 10
    game_mode: str = 'classic'
    get_period: Optional[int] = None
    inflation: bool = True

    checkers_path: str = '/checkers/'
    env_path: str = ''


class Task(BaseModel):
    checker: str
    name: str
    checker_type: str = 'hackerdom'
    checker_timeout: int = 15
    gets: int = 1
    puts: int = 1
    places: int = 1


class Team(BaseModel):
    ip: str
    name: str
    highlighted: bool = False


class BasicConfig(BaseModel):
    admin: Optional[AdminConfig]
    global_: GlobalConfig
    tasks: List[Task]
    teams: List[Team]

    class Config:
        allow_population_by_field_name = True
        fields = {
            'global_': 'global',
        }


class Config(BasicConfig):
    admin: AdminConfig
    storages: StoragesConfig

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


class GameConfig(BaseModel):
    flag_lifetime: int
    round_time: int
    start_time: datetime

    timezone: str = 'UTC'
    default_score: Union[int, float] = 2500
    game_hardness: Union[int, float] = 10
    mode: str = 'classic'
    get_period: Optional[int] = None
    inflation: bool = True

    checkers_path: str = '/checkers/'
    env_path: str = '/checkers/bin/'


class Task(BaseModel):
    name: str
    checker: str
    gets: int
    puts: int
    places: int
    checker_timeout: int
    checker_type: str = 'hackerdom'
    env_path: str = ''
    default_score: Optional[float]
    get_period: Optional[int]


class Team(BaseModel):
    ip: str
    name: str
    highlighted: bool = False


class BasicConfig(BaseModel):
    admin: Optional[AdminConfig]
    game: GameConfig
    tasks: List[Task]
    teams: List[Team]


class Config(BasicConfig):
    admin: AdminConfig
    storages: StoragesConfig

from datetime import datetime
from typing import List, Optional

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
    default_score: float = 2500
    game_hardness: float = 10
    mode: str = 'classic'
    get_period: Optional[int] = None
    inflation: bool = True
    volga_attacks_mode: bool = False

    checkers_path: str = '/checkers/'
    env_path: str = ''


class Task(BaseModel):
    name: str
    checker: str
    gets: int = 1
    puts: int = 1
    places: int = 1
    checker_timeout: int = 10
    checker_type: str = 'hackerdom'
    env_path: Optional[str] = None
    default_score: Optional[float] = None
    get_period: Optional[int] = None


class Team(BaseModel):
    ip: str
    name: str
    highlighted: bool = False


class BasicConfig(BaseModel):
    admin: Optional[AdminConfig] = None
    game: GameConfig
    tasks: List[Task]
    teams: List[Team]


class Config(BasicConfig):
    admin: AdminConfig
    storages: StoragesConfig

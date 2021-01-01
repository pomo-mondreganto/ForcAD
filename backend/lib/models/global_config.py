import datetime
from typing import Optional

from .base import BaseModel


class GlobalConfig(BaseModel):
    """Model representing global config"""
    id: Optional[int]
    flag_lifetime: int
    game_hardness: float
    inflation: bool
    round_time: int
    game_mode: str
    timezone: str
    start_time: datetime.datetime

    real_round: Optional[int]
    game_running: Optional[bool]

    table_name = 'GlobalConfig'

    __slots__ = (
        'id',
        'flag_lifetime',
        'game_hardness',
        'inflation',
        'round_time',
        'game_mode',
        'timezone',
        'start_time',
        'real_round',
        'game_running',
    )

    def __str__(self) -> str:
        return str(self.to_dict())

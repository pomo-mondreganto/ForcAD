from typing import Optional, List, Dict, Any

from kombu.utils import json as kjson

from .base import BaseModel
from .flag import Flag
from .verdict import CheckerVerdict


class Task(BaseModel):
    """
    Model representing a task.

    It also stores checker-specific info
    (path, env, number of gets, puts, flag places), etc...
    """

    id: Optional[int]
    name: str
    checker: str
    gets: int
    puts: int
    places: int
    checker_timeout: int
    checker_type: str
    env_path: str
    default_score: float
    get_period: int
    active: bool

    table_name = 'Tasks'

    defaults = {
        'active': True,
    }

    __slots__ = (
        'id',
        'name',
        'checker',
        'gets',
        'puts',
        'places',
        'checker_timeout',
        'env_path',
        'checker_type',
        'get_period',
        'default_score',
        'active',
    )

    def to_dict_for_participants(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
        }

    def to_json_for_participants(self) -> str:
        return kjson.dumps(self.to_dict_for_participants())  # type: ignore

    @property
    def checker_tags(self) -> List[str]:
        return self.checker_type.split('_')

    @property
    def checker_returns_flag_id(self) -> bool:
        return 'nfr' not in self.checker_tags

    @property
    def checker_provides_public_flag_data(self) -> bool:
        return 'pfr' in self.checker_tags

    def set_flag_data(self, flag: Flag, verdict: CheckerVerdict) -> Flag:
        if not self.checker_returns_flag_id:
            flag.public_flag_data = ''
        elif self.checker_provides_public_flag_data:
            flag.public_flag_data = verdict.public_message
            flag.private_flag_data = verdict.private_message
        else:
            flag.public_flag_data = ''
            flag.private_flag_data = verdict.public_message

        return flag

    def __str__(self) -> str:
        return f"Task({self.id}, {self.name})"

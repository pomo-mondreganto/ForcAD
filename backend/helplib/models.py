import secrets

import datetime
import yaml
from kombu.utils import json as kjson
from typing import Optional, List

from helplib.types import Action, TaskStatus


# noinspection SqlResolve
class Model(object):
    """Generic model implementing basic methods to load and print"""

    __slots__ = ()
    table_name = 'undefined'
    defaults = {}

    def __init__(self, **kwargs):
        for attr in self.__slots__:
            if attr == 'id':
                setattr(self, attr, kwargs.get(attr))
                continue
            if attr not in kwargs:
                if attr not in self.defaults:
                    raise KeyError(
                        f'Attribute {attr} is required '
                        f'for model {self.__class__}'
                    )
                setattr(self, attr, self.defaults[attr])
            else:
                setattr(self, attr, kwargs[attr])

    @classmethod
    def from_json(cls, json_str: str):
        d = kjson.loads(json_str)
        return cls(**d)

    @classmethod
    def from_yaml(cls, yaml_obj):
        d = yaml.safe_load(yaml_obj)
        return cls(**d)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def to_json(self):
        return kjson.dumps(self.to_dict())

    @classmethod
    def _get_column_names(cls):
        return list(filter(lambda x: x != 'id', cls.__slots__))

    @classmethod
    def get_select_all_query(cls):
        return f'SELECT * FROM {cls.table_name}'

    @classmethod
    def get_select_one_query(cls):
        return f'SELECT * FROM {cls.table_name} WHERE id=%(id)s'

    @classmethod
    def get_select_active_query(cls):
        return f'SELECT * FROM {cls.table_name} WHERE active=TRUE'

    @classmethod
    def get_insert_query(cls):
        column_names = cls._get_column_names()
        columns = ', '.join(column_names)
        values = ', '.join(f'%({column})s' for column in column_names)
        q = (
            f'INSERT INTO {cls.table_name} ({columns}) '
            f'VALUES ({values}) RETURNING id'
        )
        return q

    @classmethod
    def get_update_query(cls):
        column_names = cls._get_column_names()
        update_data = ', '.join(
            f'{column}=%({column})s' for column in column_names
        )
        return f'UPDATE {cls.table_name} SET {update_data} WHERE id=%(id)s'

    @classmethod
    def get_delete_query(cls):
        return f'UPDATE {cls.table_name} SET active=FALSE WHERE id=%(id)s'

    def __repr__(self):
        return str(self)


class Team(Model):
    """Model representing a team"""
    id: Optional[int]
    name: str
    ip: str
    token: str
    highlighted: bool
    active: bool

    table_name = 'Teams'

    defaults = {
        'highlighted': False,
        'active': True,
    }

    __slots__ = (
        'id',
        'name',
        'ip',
        'token',
        'highlighted',
        'active',
    )

    @staticmethod
    def generate_token():
        return secrets.token_hex(8)

    def to_dict_for_participants(self):
        d = self.to_dict()
        d.pop('token', None)
        return d

    def __str__(self):
        return f"Team({self.id, self.name})"


class Task(Model):
    """Model representing a task

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

    def to_dict_for_participants(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def to_json_for_participants(self):
        return kjson.dumps(self.to_dict_for_participants())

    @property
    def checker_tags(self):
        return self.checker_type.split('_')

    @property
    def is_checker_gevent_optimized(self):
        return 'gevent' in self.checker_tags

    @property
    def checker_returns_flag_id(self):
        return 'nfr' not in self.checker_tags

    @property
    def checker_provides_public_flag_data(self):
        return 'pfr' in self.checker_tags

    def set_flag_data(self, flag: 'Flag', verdict: 'CheckerVerdict'):
        if not self.checker_returns_flag_id:
            flag.public_flag_data = ''
        elif self.checker_provides_public_flag_data:
            flag.public_flag_data = verdict.public_message
            flag.private_flag_data = verdict.private_message
        else:
            flag.public_flag_data = ''
            flag.private_flag_data = verdict.public_message

        return flag

    def __str__(self):
        return f"Task({self.id}, {self.name})"


class Flag(Model):
    """Model representing a flag

        Contains flag round, id, team, task, the value itself
        and additional data for the checker
    """
    round: int
    id: Optional[int]
    team_id: int
    task_id: int
    flag: str
    public_flag_data: Optional[str]
    private_flag_data: Optional[str]
    vuln_number: Optional[int]

    table_name = 'Flags'

    __slots__ = (
        'id',
        'team_id',
        'task_id',
        'flag',
        'round',
        'public_flag_data',
        'private_flag_data',
        'vuln_number',
    )

    def __str__(self):
        return f"Flag({self.id}, task {self.task_id}, team {self.team_id})"


class GameState(Model):
    """Model representing game state

        Stored round and dict of team tasks
    """
    round_start: int
    round: int
    team_tasks: List[dict]

    __slots__ = ('round_start', 'round', 'team_tasks')

    def __str__(self):
        return f"GameState for round {self.round}: {self.to_dict()}"


class CheckerVerdict(Model):
    """Model representing checker action result"""
    private_message: str
    public_message: str
    command: str
    status: TaskStatus
    action: Action

    __slots__ = (
        'public_message',
        'private_message',
        'command',
        'status',
        'action',
    )

    def __init__(self, **kwargs):
        super(CheckerVerdict, self).__init__(**kwargs)
        if isinstance(self.status, int):
            self.status = TaskStatus(self.status)

    def __str__(self):
        return f'CheckerVerdict ({self.action} {self.status.name})'


class GlobalConfig(Model):
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

    def __str__(self):
        return str(self.to_dict())


class AttackResult(Model):
    attacker_id: int
    victim_id: int
    task_id: int
    submit_ok: bool
    message: str
    attacker_delta: float
    victim_delta: float

    __slots__ = (
        'attacker_id',
        'victim_id',
        'task_id',
        'submit_ok',
        'message',
        'attacker_delta',
        'victim_delta',
    )

    defaults = {
        'victim_id': 0,
        'task_id': 0,
        'submit_ok': False,
        'message': '',
        'attacker_delta': 0.0,
        'victim_delta': 0.0,
    }

    labels = ('attacker_id', 'victim_id', 'task_id', 'submit_ok')

    def get_label_key(self):
        return tuple(getattr(self, k) for k in self.labels)

    def get_label_values(self):
        return {k: getattr(self, k) for k in self.labels}

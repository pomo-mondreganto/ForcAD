import json

import yaml
from typing import Optional, List

import helplib.status


class Model(object):
    """Generic model implementing basic methods to load and print"""

    def __init__(self, *_args, **_kwargs):
        pass

    @classmethod
    def from_json(cls, json_str: str):
        d = json.loads(json_str)
        return cls(**d)

    @classmethod
    def from_yaml(cls, yaml_obj):
        d = yaml.load(yaml_obj, Loader=yaml.FullLoader)
        return cls(**d)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    def to_dict(self):
        raise NotImplemented

    def to_json(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return str(self)


class Team(Model):
    """Model representing a team"""
    id: Optional[int]
    name: str
    ip: str
    token: str

    def __init__(self, id: Optional[int], name: str, ip: str, token: str):
        super(Team, self).__init__()
        self.id = id
        self.name = name
        self.ip = ip
        self.token = token

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'token': self.token,
        }

    def to_dict_for_participants(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
        }

    def __str__(self):
        return f"Team({self.id, self.name})"


class Task(Model):
    """Model representing a task

        It also stores checker-specific info (path, env, number of gets, puts, flag places), etc...
    """
    id: Optional[int]
    name: str
    checker: str
    gets: int
    puts: int
    places: int
    checker_timeout: int
    checker_returns_flag_id: bool
    gevent_optimized: bool
    env_path: str
    default_score: Optional[float]
    get_period: int

    def __init__(self,
                 id: Optional[int],
                 name: str,
                 checker: str,
                 gets: int,
                 puts: int,
                 places: int,
                 checker_timeout: int,
                 checker_returns_flag_id: bool,
                 gevent_optimized: bool,
                 env_path: str,
                 get_period: int,
                 default_score: Optional[float] = None):
        super(Task, self).__init__()
        self.id = id
        self.name = name
        self.checker = checker
        self.gets = gets
        self.puts = puts
        self.places = places
        self.checker_timeout = checker_timeout
        self.checker_returns_flag_id = checker_returns_flag_id
        self.gevent_optimized = gevent_optimized
        self.env_path = env_path
        self.default_score = default_score
        self.get_period = get_period

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'checker': self.checker,
            'gets': self.gets,
            'puts': self.puts,
            'places': self.places,
            'checker_timeout': self.checker_timeout,
            'checker_returns_flag_id': self.checker_returns_flag_id,
            'gevent_optimized': self.gevent_optimized,
            'env_path': self.env_path,
            'default_score': self.default_score,
            'get_period': self.get_period,
        }

    def to_dict_for_participants(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def to_json_for_participants(self):
        return json.dumps(self.to_dict_for_participants())

    def __str__(self):
        return f"Task({self.id, self.name})"


class Flag(Model):
    """Model representing a flag

        Contains flag round, id, team, task, the value itself and additional data for the checker
    """
    round: int
    id: Optional[int]
    team_id: int
    task_id: int
    flag: str
    flag_data: Optional[str]
    vuln_number: Optional[int]

    def __init__(self,
                 id: Optional[int],
                 team_id: int,
                 task_id: int,
                 flag: str,
                 round: int,
                 flag_data: Optional[str],
                 vuln_number: Optional[int]):
        super(Flag, self).__init__()
        self.id = id
        self.team_id = team_id
        self.flag = flag
        self.round = round
        self.flag_data = flag_data
        self.task_id = task_id
        self.vuln_number = vuln_number

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'task_id': self.task_id,
            'flag': self.flag,
            'round': self.round,
            'flag_data': self.flag_data,
            'vuln_number': self.vuln_number,
        }

    def __str__(self):
        return (
            f"Flag({self.id}, task {self.task_id}) "
            f"{self.flag} of team {self.team_id} on round {self.round}, "
            f"data {self.flag_data}, vuln {self.vuln_number}"
        )


class GameState(Model):
    """Model representing game state

        Stored round and dict of team tasks
    """
    round_start: int
    round: int
    team_tasks: List[dict]

    def __init__(self, round_start: int, round: int, team_tasks: List[dict]):
        super(GameState, self).__init__()
        self.round_start = round_start
        self.round = round
        self.team_tasks = team_tasks

    def to_dict(self):
        return {
            'round_start': self.round_start,
            'round': self.round,
            'team_tasks': self.team_tasks
        }

    def __str__(self):
        return f"GameState for round {self.round}"


class CheckerVerdict(Model):
    """Model representing checker action result"""
    private_message: str
    public_message: str
    command: str
    status: helplib.status.TaskStatus
    action: str

    def __init__(self,
                 private_message: str,
                 public_message: str,
                 command: str,
                 action: str,
                 status: helplib.status.TaskStatus):
        super(CheckerVerdict, self).__init__()
        self.private_message = private_message
        self.public_message = public_message
        self.command = command

        if isinstance(status, int):
            self.status = helplib.status.TaskStatus(status)
        else:
            self.status = status

        self.action = action

    def to_dict(self):
        return {
            'private_message': self.private_message,
            'public_message': self.public_message,
            'command': self.command,
            'status': self.status.value,
            'action': self.action,
        }

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

    def __init__(self,
                 id: Optional[int],
                 flag_lifetime: int,
                 game_hardness: float,
                 inflation: bool,
                 round_time: int,
                 game_mode: str):
        super(GlobalConfig, self).__init__()
        self.id = id
        self.flag_lifetime = flag_lifetime
        self.game_hardness = game_hardness
        self.inflation = inflation
        self.round_time = round_time
        self.game_mode = game_mode

    def to_dict(self):
        return {
            'id': self.id,
            'flag_lifetime': self.flag_lifetime,
            'game_hardness': self.game_hardness,
            'inflation': self.inflation,
            'round_time': self.round_time,
            'game_mode': self.game_mode,
        }

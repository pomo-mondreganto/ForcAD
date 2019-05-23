import json
from typing import Optional, List

import yaml

import helpers.status


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
    env_path: str
    default_score: Optional[float]

    def __init__(self,
                 id: Optional[int],
                 name: str,
                 checker: str,
                 gets: int,
                 puts: int,
                 places: int,
                 checker_timeout: int,
                 checker_returns_flag_id: bool,
                 env_path: str,
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
        self.env_path = env_path
        self.default_score = default_score

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
            'env_path': self.env_path,
            'default_score': self.default_score,
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

    def __init__(self,
                 id: Optional[int],
                 team_id: int,
                 task_id: int,
                 flag: str,
                 round: int,
                 flag_data: Optional[str]):
        super(Flag, self).__init__()
        self.id = id
        self.team_id = team_id
        self.flag = flag
        self.round = round
        self.flag_data = flag_data
        self.task_id = task_id

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'task_id': self.task_id,
            'flag': self.flag,
            'round': self.round,
            'flag_data': self.flag_data,
        }

    def __str__(self):
        return (
            f"Flag({self.id}, task {self.task_id}) "
            f"{self.flag} of team {self.team_id} on round {self.round}, "
            f"data {self.flag_data}"
        )


class GameState(Model):
    """Model representing game state

        Stored round and dict of team tasks
    """
    round: int
    team_tasks: List[dict]

    def __init__(self, round: int, team_tasks: List[dict]):
        super(GameState, self).__init__()
        self.round = round
        self.team_tasks = team_tasks

    def to_dict(self):
        return {
            'round': self.round,
            'team_tasks': self.team_tasks
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return f"GameState for round {self.round}"


class CheckerActionResult(Model):
    """Model representing checker action result"""
    private_message: str
    public_message: str
    command: List
    status: helpers.status.TaskStatus

    def __init__(self,
                 private_message: str,
                 public_message: str,
                 command: List,
                 status: helpers.status.TaskStatus):
        super(CheckerActionResult, self).__init__()
        self.private_message = private_message
        self.public_message = public_message
        self.command = command
        self.status = status

    def to_dict(self):
        return {
            'private_message': self.private_message,
            'public_message': self.public_message,
            'command': self.command,
            'status': self.status.value,
        }

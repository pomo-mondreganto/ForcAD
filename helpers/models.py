import json
from typing import Optional

import yaml


class Model(object):
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


class Team(Model):
    id: Optional[int]
    name: str
    ip: str

    def __init__(self, id: Optional[int], name: str, ip: str):
        super(Team, self).__init__()
        self.id = id
        self.name = name
        self.ip = ip

    def to_json(self):
        d = {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
        }
        return json.dumps(d)


class Task(Model):
    id: Optional[int]
    name: str
    checker: str
    gets: int
    puts: int
    places: int
    checker_timeout: int
    env_path: str

    def __init__(self,
                 id: Optional[int],
                 name: str,
                 checker: str,
                 gets: int,
                 puts: int,
                 places: int,
                 checker_timeout: int,
                 env_path: str):
        super(Task, self).__init__()
        self.id = id
        self.name = name
        self.checker = checker
        self.gets = gets
        self.puts = puts
        self.places = places
        self.checker_timeout = checker_timeout
        self.env_path = env_path

    def to_json(self):
        d = {
            'id': self.id,
            'name': self.name,
            'checker': self.checker,
            'gets': self.gets,
            'puts': self.puts,
            'places': self.places,
            'checker_timeout': self.checker_timeout,
            'env_path': self.env_path,
        }
        return json.dumps(d)

    def __str__(self):
        return f"Task({self.id, self.name})"

    def __repr__(self):
        return str(self)


class Flag(Model):
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

    def to_json(self):
        d = {
            'id': self.id,
            'team_id': self.team_id,
            'task_id': self.task_id,
            'flag': self.flag,
            'round': self.round,
            'flag_data': self.flag_data,
        }
        return json.dumps(d)

    def __str__(self):
        return (
            f"Flag({self.id}, task {self.task_id}) "
            f"{self.flag} of team {self.team_id} on round {self.round}, "
            f"data {self.flag_data}"
        )

    def __repr__(self):
        return str(self)

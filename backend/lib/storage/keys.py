from typing import Union


class CacheKeys:
    @staticmethod
    def round_start(r: int) -> str:
        return f'round:{r}:start_time'

    @staticmethod
    def current_round() -> str:
        return 'real_round'

    @staticmethod
    def game_config() -> str:
        return 'game_config'

    @staticmethod
    def game_state() -> str:
        return 'game_state'

    @staticmethod
    def teams() -> str:
        return 'teams'

    @staticmethod
    def team_by_token(token: str) -> str:
        return f'team:token:{token}'

    @staticmethod
    def team_stolen_flags(team_id: int) -> str:
        return f'team:{team_id}:stolen_flags'

    @staticmethod
    def tasks() -> str:
        return 'tasks'

    @staticmethod
    def flags_cached() -> str:
        return 'flags:cached'

    @staticmethod
    def flag_by_field(field: str, value: Union[str, int]):
        return f'flag:{field}:{value}'

    @classmethod
    def flag_by_id(cls, flag_id: int) -> str:
        return cls.flag_by_field('id', flag_id)

    @classmethod
    def flag_by_str(cls, flag_str: str) -> str:
        return cls.flag_by_field('str', flag_str)

    @staticmethod
    def attack_data() -> str:
        return 'attack_data'

    @staticmethod
    def teamtasks(team_id: int, task_id: int) -> str:
        return f'teamtasks:{team_id}:{task_id}'

    @staticmethod
    def session(session_key: str) -> str:
        return f'session:{session_key}'

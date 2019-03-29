import secrets
import string

import storage
from helpers import models

ALPHABET = string.ascii_uppercase + string.digits


def generate_flag(service: str, team_id: int, task_id: int, round: int) -> models.Flag:
    flag_text = f"{service[0].upper()}{''.join(secrets.choice(ALPHABET) for _ in range(30))}="
    return models.Flag(id=None, team_id=team_id, task_id=task_id, flag=flag_text, round=round, flag_data=None)


def check_flag(flag_str: str, attacker: int, round: int) -> models.Flag:
    flag = storage.flags.get_flag_by_str(flag_str=flag_str, round=round)
    storage.flags.check_flag(flag=flag, attacker=attacker, round=round)
    return flag

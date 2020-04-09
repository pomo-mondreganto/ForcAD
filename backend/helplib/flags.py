import secrets
import string

import storage
from helplib import models

ALPHABET = string.ascii_uppercase + string.digits


def generate_flag(service: str, team_id: int, task_id: int, round: int) -> models.Flag:
    """Generate a new flag

        :param service: service name of new flag (to pick first flag letter)
        :param team_id: team id
        :param task_id: task id
        :param round: current round
        :return: Flag model instance
    """
    flag_text = f"{service[0].upper()}{''.join(secrets.choice(ALPHABET) for _ in range(30))}="

    return models.Flag(
        id=None,
        team_id=team_id,
        task_id=task_id,
        flag=flag_text,
        round=round,
        public_flag_data=None,
        private_flag_data=None,
        vuln_number=None,
    )


def try_add_stolen_flag_by_str(flag_str: str, attacker: int, round: int) -> models.Flag:
    """Check flag wrapper, fetching flag using its string value, then runs try_add_stolen_flag from storage"""
    flag = storage.flags.get_flag_by_str(flag_str=flag_str, round=round)
    storage.flags.try_add_stolen_flag(flag=flag, attacker=attacker, round=round)
    return flag

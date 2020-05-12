import secrets
import string

from helplib import models

ALPHABET = string.ascii_uppercase + string.digits


def generate_flag(service: str,
                  team_id: int,
                  task_id: int,
                  current_round: int) -> models.Flag:
    """Generate a new flag

        :param service: service name of new flag (to pick first flag letter)
        :param team_id: team id
        :param task_id: task id
        :param current_round: current round
        :return: Flag model instance
    """
    service_letter = service[0].upper()
    rnd_data = ''.join(secrets.choice(ALPHABET) for _ in range(30))
    flag_text = service_letter + rnd_data + '='

    return models.Flag(
        id=None,
        team_id=team_id,
        task_id=task_id,
        flag=flag_text,
        round=current_round,
        public_flag_data=None,
        private_flag_data=None,
        vuln_number=None,
    )

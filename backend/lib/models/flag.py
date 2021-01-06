import secrets
import string

from typing import Optional

from .base import BaseModel

ALPHABET = string.ascii_uppercase + string.digits


class Flag(BaseModel):
    """
    Model representing a flag.

    Contains flag round, id, team, task, the value itself
    and additional data for the checker.
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

    @classmethod
    def generate(
            cls, service: str, team_id: int, task_id: int, current_round: int
    ) -> 'Flag':
        """
        Generate a new flag.

        :param service: service of new flag (to pick the first flag letter)
        :param team_id: team id
        :param task_id: task id
        :param current_round: current round
        :return: Flag model instance
        """
        service_letter = service[0].upper()
        rnd_data = ''.join(secrets.choice(ALPHABET) for _ in range(30))
        flag_text = service_letter + rnd_data + '='

        return cls(
            id=None,
            team_id=team_id,
            task_id=task_id,
            flag=flag_text,
            round=current_round,
            public_flag_data=None,
            private_flag_data=None,
            vuln_number=None,
        )

    def __str__(self) -> str:
        return f"Flag({self.id}, task {self.task_id}, team {self.team_id})"

import secrets
from typing import Optional, Dict, Any

from .base import BaseModel


class Team(BaseModel):
    """Model representing a team."""

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
    def generate_token() -> str:
        return secrets.token_hex(8)

    def to_dict_for_participants(self) -> Dict[str, Any]:
        d = self.to_dict()
        d.pop('token', None)
        return d

    def __str__(self) -> str:
        return f"Team({self.id}, {self.name})"

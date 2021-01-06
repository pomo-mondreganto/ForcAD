from typing import List, Dict, Any

from .base import BaseModel


class GameState(BaseModel):
    """Model representing the game state."""

    round_start: int
    round: int
    team_tasks: List[Dict[str, Any]]

    __slots__ = ('round_start', 'round', 'team_tasks')

    def __str__(self) -> str:
        return f"GameState for round {self.round}: {self.to_dict()}"

from typing import Any

from .base import BaseModel
from .types import Action, TaskStatus


class CheckerVerdict(BaseModel):
    """Model representing checker action result."""

    private_message: str
    public_message: str
    command: str
    status: TaskStatus
    action: Action

    __slots__ = (
        'public_message',
        'private_message',
        'command',
        'status',
        'action',
    )

    def __init__(self, **kwargs: Any):
        super(CheckerVerdict, self).__init__(**kwargs)
        if isinstance(self.status, int):
            self.status = TaskStatus(self.status)

    def __str__(self) -> str:
        return f'CheckerVerdict ({self.action} {self.status.name})'

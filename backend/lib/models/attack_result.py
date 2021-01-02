from typing import Dict, Any, Tuple

from .base import BaseModel


class AttackResult(BaseModel):
    attacker_id: int
    victim_id: int
    task_id: int
    submit_ok: bool
    message: str
    attacker_delta: float
    victim_delta: float

    __slots__ = (
        'attacker_id',
        'victim_id',
        'task_id',
        'submit_ok',
        'message',
        'attacker_delta',
        'victim_delta',
    )

    defaults = {
        'victim_id': 0,
        'task_id': 0,
        'submit_ok': False,
        'message': '',
        'attacker_delta': 0.0,
        'victim_delta': 0.0,
    }

    labels = ('attacker_id', 'victim_id', 'task_id', 'submit_ok')

    def get_label_key(self) -> Tuple[Any, ...]:
        return tuple(getattr(self, k) for k in self.labels)

    def get_label_values(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.labels}

    def get_flag_notification(self) -> Dict[str, Any]:
        return {
            'attacker_id': self.attacker_id,
            'victim_id': self.victim_id,
            'task_id': self.task_id,
            'attacker_delta': self.attacker_delta,
        }

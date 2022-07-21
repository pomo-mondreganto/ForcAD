from typing import List

import eventlet

from lib import storage
from lib.models import AttackResult
from .notifier import Notifier
from .submit_monitor import SubmitMonitor


class Judge:
    def __init__(self, monitor: SubmitMonitor, logger):
        self._monitor = monitor
        self._notifier = Notifier(logger=logger)
        eventlet.spawn_n(self._monitor)
        eventlet.spawn_n(self._notifier)

    def _process_attack(self, team_id: int, flag: str) -> AttackResult:
        current_round = storage.game.get_real_round()
        ar = storage.attacks.handle_attack(
            attacker_id=team_id,
            flag_str=flag,
            current_round=current_round,
        )

        if ar.submit_ok:
            self._notifier.add(ar)
            self._monitor.inc_ok()
        else:
            self._monitor.inc_bad()

        return ar

    def process(self, team_id: int, flag: str) -> AttackResult:
        return self._process_attack(team_id, flag)

    def process_many(self, team_id: int, flags: List[str]) -> List[AttackResult]:
        return [self._process_attack(team_id, flag) for flag in flags]

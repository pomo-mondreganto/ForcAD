from eventlet.greenpool import GreenPool
from typing import List

from lib import storage
from lib.models import AttackResult
from .notifier import Notifier
from .submit_monitor import SubmitMonitor


class Judge:
    def __init__(self,
                 monitor: SubmitMonitor,
                 logger,
                 concurrency=2000):
        self._monitor = monitor
        self._notifier = Notifier(logger=logger)
        self._p = GreenPool(size=concurrency)
        self._p.spawn_n(self._monitor)
        self._p.spawn_n(self._notifier)

    def _process_attack(self, team_id: int, flag: str) -> AttackResult:
        current_round = storage.game.get_real_round()
        ar = storage.attacks.handle_attack(
            attacker_id=team_id,
            flag_str=flag,
            current_round=current_round,
        )

        if ar.submit_ok:
            self._notifier.add(ar)
        self._monitor.add(ar)

        return ar

    def process(self, team_id: int, flag: str) -> AttackResult:
        result = self._p.spawn(self._process_attack, team_id, flag)
        return result.wait()

    def process_many(self,
                     team_id: int,
                     flags: List[str]) -> List[AttackResult]:
        results = self._p.imap(
            lambda flag: self._process_attack(team_id, flag),
            flags,
        )
        return list(results)

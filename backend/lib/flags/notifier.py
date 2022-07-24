from logging import Logger

import eventlet
from eventlet.queue import LightQueue, Empty, Full

from lib import storage
from lib.models import AttackResult


class Notifier:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._q = LightQueue(maxsize=1000)

        # ensure no one is writing to the same broker connection concurrently
        self._sio = storage.utils.SIOManager.create(write_only=True)

    def _process(self, ar: AttackResult):
        flag_data = ar.get_flag_notification()
        self._logger.debug('Sending notification with %s', flag_data)
        self._sio.emit(
            event='flag_stolen',
            data={'data': flag_data},
            namespace='/live_events',
        )

    def add(self, ar: AttackResult) -> bool:
        try:
            self._q.put_nowait(ar)
            return True
        except Full:
            return False

    def __call__(self) -> None:
        while True:
            try:
                ar = self._q.get(block=True, timeout=3)
            except Empty:
                eventlet.sleep(0.5)
            else:
                self._process(ar)

from logging import Logger

from eventlet.greenpool import GreenPool

from lib import storage
from lib.models import AttackResult


class Notifier:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._pool = GreenPool(size=100)

    def _process(self, ar: AttackResult):
        flag_data = ar.get_flag_notification()
        self._logger.debug('Sending notification with %s', flag_data)
        storage.utils.get_wro_sio_manager().emit(
            event='flag_stolen',
            data={'data': flag_data},
            namespace='/live_events',
        )

    def add(self, ar: AttackResult) -> None:
        self._pool.spawn_n(self._process, ar)

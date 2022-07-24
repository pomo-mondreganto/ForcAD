from logging import Logger

import eventlet


class SubmitMonitor:
    def __init__(self, logger: Logger, interval: float = 10):
        self._logger = logger

        self._ok_submits = 0
        self._bad_submits = 0
        self._requests = 0

        self._interval = interval

        self._was_ok = self._ok_submits
        self._was_bad = self._bad_submits
        self._was_requests = self._requests

    def inc_ok(self) -> None:
        self._ok_submits += 1

    def inc_bad(self) -> None:
        self._bad_submits += 1

    def inc_requests(self) -> None:
        self._requests += 1

    def _process_statistics(self) -> None:
        new_ok, new_bad = self._ok_submits, self._bad_submits
        new_requests = self._requests
        self._logger.info(
            f"OK: {new_ok - self._was_ok:>6}, "
            f"BAD: {new_bad - self._was_bad:>6}, "
            f"REQ: {new_requests - self._was_requests:>6}, "
            f"TOTOK: {new_ok:>6}, TOTBAD: {new_bad:>6}, "
            f"TOTREQ: {new_requests:>6}"
        )
        self._was_ok = new_ok
        self._was_bad = new_bad
        self._was_requests = new_requests

    def __call__(self) -> None:
        while True:
            try:
                self._process_statistics()
            except Exception as e:
                self._logger.error("Error in monitoring: %s", str(e))
            eventlet.sleep(self._interval)

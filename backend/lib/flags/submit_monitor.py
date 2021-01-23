from collections import defaultdict
from logging import Logger

import eventlet
from eventlet.queue import Queue, Empty
from kombu import Connection
from kombu.messaging import Producer

from lib import models, config


class SubmitMonitor:
    def __init__(self, logger: Logger, interval: float = 10):
        self._logger = logger
        self._q = Queue()

        self._ok_submits = 0
        self._bad_submits = 0
        self._connections = 0

        self._interval = interval

        self._was_ok = self._ok_submits
        self._was_bad = self._bad_submits
        self._was_conn = self._connections

        self._labels = ['attacker_id', 'victim_id', 'task_id', 'submit_ok']

    def add(self, ar: models.AttackResult) -> None:
        self._q.put_nowait(ar)
        if ar.submit_ok:
            self.inc_ok()
        else:
            self.inc_bad()

    def inc_ok(self) -> None:
        self._ok_submits += 1

    def inc_bad(self) -> None:
        self._bad_submits += 1

    def inc_conns(self) -> None:
        self._connections += 1

    def _process_statistics(self) -> None:
        new_ok, new_bad = self._ok_submits, self._bad_submits
        new_conn = self._connections
        self._logger.info(
            f"OK: {new_ok - self._was_ok:>6}, "
            f"BAD: {new_bad - self._was_bad:>6}, "
            f"CONN: {new_conn - self._was_conn:>6}, "
            f"TOTOK: {new_ok:>6}, TOTBAD: {new_bad:>6}, "
            f"TOTCONN: {new_conn:>6}"
        )
        self._was_ok = new_ok
        self._was_bad = new_bad
        self._was_conn = new_conn

    def _process_attacks_queue(self) -> None:
        conn = Connection(config.get_broker_url())
        with conn.channel() as channel:
            producer = Producer(channel)
            by_label = defaultdict(list)
            while not self._q.empty():
                try:
                    ar: models.AttackResult = self._q.get_nowait()
                except Empty:
                    continue
                else:
                    by_label[ar.get_label_key()].append(ar)

            for ar_list in by_label.values():
                if not ar_list:
                    continue

                monitor_message = {
                    'type': 'flag_submit',
                    'data': ar_list[0].get_label_values(),
                    'value': len(ar_list),
                }

                producer.publish(
                    monitor_message,
                    exchange='',
                    routing_key='forcad-monitoring',
                )

    def __call__(self) -> None:
        while True:
            try:
                self._process_statistics()
                self._process_attacks_queue()
            except Exception as e:
                self._logger.error("Error in monitoring: %s", str(e))
            eventlet.sleep(self._interval)

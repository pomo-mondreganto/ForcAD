import socket

from flask import Flask, make_response
from kombu import Message, Queue, Consumer
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
)
from prometheus_client.exposition import generate_latest

from lib import storage


class MetricsServer:
    def __init__(self, app: Flask):
        self.app = app
        self.flag_submits_metric = Counter(
            name='flag_submits_total',
            documentation='Flag submission data',
            labelnames=['attacker_id', 'victim_id', 'task_id', 'submit_ok'],
        )

    @staticmethod
    def _get_data() -> str:
        return generate_latest(REGISTRY)

    def add_endpoint(self, path: str):
        def monitoring_endpoint():
            response = make_response(self._get_data())
            response.headers['Content-Type'] = CONTENT_TYPE_LATEST
            return response

        self.app.add_url_rule(path, 'metrics', monitoring_endpoint)

    def _process_message(self, body, message: Message):
        # ack message first, metrics don't have to be exact
        message.ack()
        if body['type'] == 'flag_submit':
            self.flag_submits_metric.labels(**body['data']).inc(
                amount=body.get('value', 1),
            )
        else:
            self.app.logger.error('Unknown metric type in %s', body)

    def consume(self, conn, queue):
        with conn.channel() as channel:
            consumer = Consumer(
                channel=channel,
                queues=[queue],
                accept=['json'],
            )
            consumer.register_callback(self._process_message)
            consumer.consume()
            while True:
                try:
                    conn.drain_events(timeout=5)
                except socket.timeout:
                    self.app.logger.debug('Timeout waiting for events')
                    conn.heartbeat_check()

    def connect_consumer(self):
        queue = Queue('forcad-monitoring')
        while True:
            with storage.utils.BrokerConnection.create() as conn:
                try:
                    self.consume(conn, queue)
                except conn.connection_errors:
                    pass

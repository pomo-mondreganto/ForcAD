import aio_pika
from kombu.utils import json as kjson
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
)
from prometheus_client.exposition import generate_latest
from sanic.response import raw

import config


class MonitorClient:
    def __init__(self, app):
        self.app = app
        self.flag_metric = Counter(
            name='flag_submits_total',
            documentation='Flag submission data',
            labelnames=['attacker_id', 'victim_id', 'task_id', 'submit_ok'],
        )

    @staticmethod
    def get_data():
        return generate_latest(REGISTRY)

    def add_endpoint(self, name):
        @self.app.route(name)
        async def monitoring_endpoint(_request):
            return raw(self.get_data(), content_type=CONTENT_TYPE_LATEST)

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                data = message.body.decode()
            except UnicodeDecodeError:
                return

            data = kjson.loads(data)
            if data['type'] == 'flag_submit':
                self.flag_metric.labels(**data['data']).inc()
            else:
                print('Unknown metric type:', data)

    async def connect_consumer(self):
        broker_url = config.get_broker_url()
        connection = await aio_pika.connect_robust(broker_url)
        queue_name = 'forcad-monitoring'
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)
        queue = await channel.declare_queue(queue_name, auto_delete=True)
        await queue.consume(self.process_message)

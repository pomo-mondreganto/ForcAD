import asyncio
from sanic import Sanic
from sanic_cors import CORS

from metrics import MetricsServer

app = Sanic('forcad_monitoring')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

loop = asyncio.get_event_loop()
metrics = MetricsServer(app)
metrics.add_endpoint('/api/metrics')
loop.run_until_complete(metrics.connect_consumer())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

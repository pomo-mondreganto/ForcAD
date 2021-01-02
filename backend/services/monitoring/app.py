import eventlet
from flask import Flask
from flask_cors import CORS

from metrics import MetricsServer

app = Flask('forcad_monitoring')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

metrics = MetricsServer(app)
metrics.add_endpoint('/api/metrics')
eventlet.spawn(metrics.connect_consumer)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

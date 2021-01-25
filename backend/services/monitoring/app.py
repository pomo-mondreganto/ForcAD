import logging

import eventlet
from flask import Flask, jsonify
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


@app.route('/api/metrics/health/')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

import logging
from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from views import receiver_bp

app = Flask('forcad_http_receiver')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)
PrometheusMetrics(
    app,
    path='/api/http-receiver/metrics',
    group_by='url_rule',
    default_latency_as_histogram=True,
)

app.register_blueprint(receiver_bp, url_prefix='/flags')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    logging.basicConfig(
        level=gunicorn_logger.level,
        handlers=gunicorn_logger.handlers,
    )

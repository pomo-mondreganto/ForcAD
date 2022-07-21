import logging
from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from viewsets import admin_bp

app = Flask('forcad_admin')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)
PrometheusMetrics(
    app,
    path='/api/admin/metrics',
    group_by='url_rule',
    default_latency_as_histogram=True,
)

app.register_blueprint(admin_bp, url_prefix='/api/admin/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    logging.basicConfig(
        level=gunicorn_logger.level,
        handlers=gunicorn_logger.handlers,
    )

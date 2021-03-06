import logging
from flask import Flask
from flask_cors import CORS

from views import client_bp

app = Flask('forcad_api')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

app.register_blueprint(client_bp, url_prefix='/api/client/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

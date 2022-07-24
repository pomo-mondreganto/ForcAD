import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from lib import storage

app = Flask('forcad_events')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

sio_manager = storage.utils.SIOManager.read_write()
sio = SocketIO(
    app=app,
    async_mode='eventlet',
    client_manager=sio_manager,
    path='socket.io',
    cors_allowed_origins='*',
)


@sio.on('connect', namespace='/game_events')
def handle_game_connect():
    app.logger.debug("New game events connection")
    scoreboard = storage.game.construct_scoreboard()
    emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
    )


@sio.on('connect', namespace='/live_events')
def handle_live_connect():
    app.logger.debug("New live events connection")


@app.route('/api/events/health/')
def health_check():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    logging.basicConfig(
        level=gunicorn_logger.level,
        handlers=gunicorn_logger.handlers,
    )

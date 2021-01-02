from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from lib import storage

app = Flask('forcad_events')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

sio_manager = storage.utils.get_sio_manager()
sio = SocketIO(
    app=app,
    async_mode='eventlet',
    client_manager=sio_manager,
    path='socket.io',
    cors_allowed_origins=[],
)


@sio.on('connect', namespace='/game_events')
def handle_connect():
    scoreboard = storage.game.construct_scoreboard()
    emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

import socketio
from sanic import Sanic
from sanic_cors import CORS

from lib import storage

app = Sanic('forcad_events')
app.enable_websocket(True)
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

sio_manager = storage.utils.get_async_sio_manager()
sio = socketio.AsyncServer(
    async_mode='sanic',
    client_manager=sio_manager,
    cors_allowed_origins=[],
)


async def emit_init_scoreboard(sid=None):
    scoreboard = await storage.game.construct_scoreboard()

    await sio.emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
        room=sid,
    )


@sio.on('connect', namespace='/game_events')
async def handle_connect(sid, _environ):
    await emit_init_scoreboard(sid)


sio.attach(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
